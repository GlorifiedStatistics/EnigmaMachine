class EnigmaMachine:
    def __init__(self, rotors, reflector, positions=None, ring_settings=None, plugboard=None):
        """
        An implementation of an enigma machine without ring settings ("Ringstellung")
        :param rotors: a list of Rotor objects. The position of the rotors will be read as if the list was you looking
            at the physical enigma machine about to use it. That is, the Rotor at index 0 would be the "last" rotor, or
            the one closest to the reflector plate, and the Rotor at index -1 would be the "first" rotor.
        :param reflector: the reflector plate
        :param plugboard: a list of strings/tuples/lists describing the plugboard on the machine (google
            "enigma machine plugboard" for information on how the plugboard functions in the machine).
            Each string should be of length 2, IE: each string is a pair of characters that are connected.
            Each tuple/list should be of length 2, and can have either single characters, or integers as mapping values.
                Integers should be in the range [0, 25], and characters in the ranges ['A', 'Z'] or ['a', 'z']
            Characters cannot map to multiple different values, IE: the two strings "RT", "RU" since they map
                to different values
        :param positions: if not None, will call self.set_positions(positions) to set the positions of the rotors
        :param ring_settings: if not None, will call self.set_ring_settings(ring_settings) to set the ring_settings
            of the rotors
        """
        self.rotors = EnigmaMachine._check_rotors(rotors)
        self.reflector = EnigmaMachine._check_reflector(reflector)
        self.plugboard = EnigmaMachine._check_plugboard(plugboard if plugboard is not None else [])
        if positions is not None:
            self.set_positions(positions)
        if ring_settings is not None:
            self.set_ring_settings(ring_settings)

    def set_positions(self, positions):
        """
        Sets the positions of the rotors
        :param positions: a list of integers or chars describing the rotor positions
        """
        if not isinstance(positions, (list, tuple)):
            raise TypeError("Positions must be a list, got type: %s" % type(positions))
        if len(positions) != len(self.rotors):
            raise ValueError("Incorrect number of positions. Found (%d) positions for (%d) rotors"
                             % (len(positions), len(self.rotors)))
        for i, p in enumerate(positions):
            self.rotors[i].set_position(p)

    def set_ring_settings(self, ring_settings):
        """
        Sets the ring_settings of the rotors
        :param ring_settings: a list of integers or chars describing the rotor ring_settings
        """
        if not isinstance(ring_settings, (list, tuple)):
            raise TypeError("Ring_settings must be a list, got type: %s" % type(ring_settings))
        if len(ring_settings) != len(self.rotors):
            raise ValueError("Incorrect number of ring_settings. Found (%d) ring_settings for (%d) rotors"
                             % (len(ring_settings), len(self.rotors)))
        for i, r in enumerate(ring_settings):
            self.rotors[i].set_ring_setting(r)

    def encode(self, string):
        """
        Runs the given string through enigma, and returns the encoded string (in uppercase)
        Can only encode the 26 letters of the alphabet (spaces are automatically removed)
        :param string: the string to encode
        :return: the encoded string
        """
        ret = ""

        for c in string.lower().replace(" ", ""):
            v = ord(c) - ord('a')

            if v < 0 or v > 25:
                raise ValueError("Can not encode the character: %s" % c)

            # Rotate the rotors first
            for r in reversed(self.rotors):
                if not r.rotate():
                    break

            # Send the signals through the plugboard
            v = self.plugboard[v]

            # Send the signals through the right side of the machine
            for r in reversed(self.rotors):
                v = r.right_side(v)

            # Bounce off the reflector plate
            v = self.reflector.reflect(v)

            # Send the signals through the left side of the machine
            for r in self.rotors:
                v = r.left_side(v)

            # Send through the plugboard once more
            v = self.plugboard[v]

            ret += chr(v + ord('a'))
        return ret.upper()

    @staticmethod
    def _check_rotors(rotors):
        """
        Checks to make sure rotors is correct
        :param rotors: the rotors
        :return: the same rotors
        """
        if not isinstance(rotors, (list, tuple)):
            raise TypeError("Rotors must be a list of rotors, got type: %s" % type(rotors))
        if len(rotors) == 0:
            raise ValueError("There must be at least one rotor")
        for r in rotors:
            if not isinstance(r, Rotor):
                raise TypeError("Each rotor must be an instance of the object Rotor, got type: %s" % type(r))
        return list(rotors)

    @staticmethod
    def _check_reflector(reflector):
        """
        Checks that the reflector is correct. This is really only here in case in the future I want to do other checks.
        :param reflector: the reflector
        :return: the same reflector
        """
        if not isinstance(reflector, Reflector):
            raise TypeError("Reflector must be an instance of the object Reflector, got type: %s" % type(reflector))
        return reflector

    @staticmethod
    def _check_plugboard(plugboard):
        """
        Checks the plugboard is correct, and returns a list where the index refers to the incoming signal letter, and
            the value at that index is the signal letter that would come out of the plugboard
        :param plugboard: a list/tuple of either tuples or strings of length 2 describing the plugboard, with no
            letters that map to multiple values.
        :return: a list of integers
        """
        if not isinstance(plugboard, (list, tuple)):
            raise TypeError("Plugboard must be a list, got type: %s" % plugboard)

        # Temporary dictionary to check there are no conflicts
        d = {}

        for p in plugboard:
            if isinstance(p, tuple):
                p = list(p)
            if isinstance(p, str):
                if len(p) != 2:
                    raise ValueError("Each string in plugboard must be of length 2, got string: \"%s\"" % p)
                p = p.lower()
                v1 = ord(p[0]) - ord('a')
                v2 = ord(p[1]) - ord('a')
                if v1 < 0 or v1 > 25 or v2 < 0 or v2 > 25:
                    raise ValueError("Each character in strings for the plugboard must be either in the range "
                                     "['A', 'Z'] or ['a', 'z'], got string \"%s\"" % p)
                p = [v1, v2]
            elif isinstance(p, list):
                if len(p) != 2:
                    raise ValueError("Tuples/lists for plugboard must be of size 2, got size: %d" % len(p))
                for i, v in enumerate(p):
                    if isinstance(v, float):
                        if v - int(v) == 0:
                            v = int(v)
                        else:
                            raise TypeError("Values in tuples/lists for plugboard must be either integer or char, "
                                            "got: %f" % v)
                    if isinstance(v, int):
                        if v < 0 or v > 25:
                            raise ValueError("Integers in tuples/lists for plugboard must be in the range [0, 25], "
                                             "got: %d" % v)
                        p[i] = v
                    elif isinstance(v, str):
                        if len(v) != 1:
                            raise ValueError("Values in tuples/lists for plugboard must be either integer or char, "
                                             "got the string: \"%s\"" % v)
                        v = v.lower()
                        vv = ord(v) - ord('a')
                        if vv < 0 or vv > 25:
                            raise ValueError("Characters in tuples/lists for plugboard must be in the range ['A', 'Z'] "
                                             "or ['a', 'z'], got: '%s'" % v)
                        p[i] = vv
                    else:
                        raise TypeError("Values in tuples/lists for plugboard must be either integer or char, "
                                        "instead got type: %s" % type(v))
            else:
                raise TypeError("Objects in plugboard must be either string, tuple, or list, got "
                                "type: %s" % type(p))

            # Now check for conflicts
            if p[0] in list(d.keys()) or p[1] in list(d.keys()):
                raise ValueError("Letters in plugboard map to different values. Found while mapping integers (%d, %d), "
                                 "or chars (%s, %s)" % (p[0], p[1], chr(p[0] + ord('a')), chr(p[1] + ord('a'))))
            d[p[0]] = p[1]
            d[p[1]] = p[0]

        # Make the dictionary into a list just because I like thinking about the plugboard as a list instead as a dict
        ret = list(range(26))
        for k in d.keys():
            ret[k] = d[k]
        return ret


class Rotor:
    def __init__(self, alphabet, turnovers, position=0, ring_setting=0):
        """
        A single rotor in the machine
        Note: the ring settings or "Ringstellung" is not implemented
        :param alphabet: the mappings of letters. Should be a string/list/tuple of size 26 where the index of the
            list/tuple would represent the incoming (from the right) signal letter, and the integer/letter would be the
            output (left side) signal letter. Can either enter letter values as integers in the range [0, 25]
            (if a list/tuple), or letters in the range ['A', 'Z'] or lowercase ['a', 'z'].
            Must contain exactly one of each letter in the alphabet.
        :param turnovers: the position or positions which will turn the next rotor. Can be a single integer/letter in
            the range [0, 25], ['A', 'Z'], or the lowercase ['a', 'z'], or can be a list/tuple of such values denoting
            multiple turnover positions.
            Duplicate turnover positions will be ignored
        :param position: the current position of the rotor, either integer or char following the rules above
        :param ring_setting: the position of the ring setting, either integer or char following the rules above
        """
        self.increments, self.reverse_increments = Rotor._check_alphabet(alphabet)
        self.turnovers = Rotor._check_turnovers(turnovers)
        self.position = Rotor._check_position(position)
        self.ring_setting = Rotor._check_ring_setting(ring_setting)

    def set_position(self, position):
        """
        Sets the position of this rotor, while checking to make sure it is a correct position
        :param position: the position to set
        """
        self.position = Rotor._check_position(position)

    def set_ring_setting(self, ring_setting):
        """
        Sets the ring_setting of this rotor, while checking to make sure it is a correct position
        :param ring_setting: the ring_setting to set
        """
        self.ring_setting = Rotor._check_ring_setting(ring_setting)

    def right_side(self, val):
        """
        Returns the signal letter that would be outputted should a signal came in at the letter val (from right to left)
        :param val: the incoming right signal letter
        :return: the outgoing left signal letter
        """
        if not isinstance(val, int) or val < 0 or val > 25:
            raise ValueError("Got erroneous val to pass through rotor: %s" % val)
        return (val + self.increments[(val + self.position - self.ring_setting) % 26]) % 26

    def left_side(self, val):
        """
        Returns the signal letter that would be outputted should a signal came in at the letter val (from left to right)
        :param val: the incoming left signal letter
        :return: the outgoing right signal letter
        """
        if not isinstance(val, int) or val < 0 or val > 25:
            raise ValueError("Got erroneous val to pass through rotor: %s" % val)
        return (val + self.reverse_increments[(val + self.position - self.ring_setting) % 26]) % 26

    def rotate(self):
        """
            Rotates the rotor one notch, and returns True if the next rotor to the left would have been rotated as well
        :return: True if the next rotor to the left would have been turned, False otherwise
        """
        ret = self.position in self.turnovers
        self.position = (self.position + 1) % 26
        return ret

    @staticmethod
    def _check_alphabet(alphabet):
        """
        Checks if the alphabet is a working alphabet, and converts to ints
        :param alphabet: the alphabet
        :return: a list/tuple of ints to use as the rotor alphabet (will be a list of increments)
        """
        if isinstance(alphabet, str):
            alphabet = [c for c in alphabet]

        if not isinstance(alphabet, (list, tuple)):
            raise TypeError("Rotor alphabet must be a list/tuple, got type: %s" % type(alphabet))

        if len(alphabet) != 26:
            raise ValueError("Rotor alphabet must be of size 26, instead got size: %d" % len(alphabet))

        ret = []

        for a in alphabet:
            if isinstance(a, float):
                if a - int(a) == 0:
                    a = int(a)
                else:
                    raise TypeError("Each element in the Rotor alphabet must either be an integer or a char"
                                    ", got value: %f" % a)
            if isinstance(a, int):
                if a < 0 or a > 25:
                    raise ValueError("Rotor alphabet integers must be in the range [0, 25], got value: %d" % a)
                ret.append(a)
            elif isinstance(a, str):
                if len(a) != 1:
                    raise ValueError("Rotor alphabet elements must be a single character, not a string: \"%s\"" %a)
                a = a.lower()
                v = ord(a) - ord('a')
                if v < 0 or v > 25:
                    raise ValueError("Rotor alphabet elements must be letters of the alphabet, got: '%s'" % a)
                ret.append(v)
            else:
                raise TypeError("Rotor alphabet elements must be either an integer or a char, instead got type: %s"
                                % type(a))

        for i in range(26):
            if i not in ret:
                raise ValueError("Rotor alphabet must contain every letter exactly once")

        # Finally, convert the alphabet into the increments, and do the reverse alphabet
        return [r - i for i, r in enumerate(ret)], \
            [r - i for i, r in enumerate([ret.index(i) for i in range(26)])]

    @staticmethod
    def _check_turnovers(turnovers):
        """
        Check whether or not this is a valid turnover or turnover list, returns a list of integers
        :param turnovers: a single integer/letter describing a turnover position, or a list of such turnovers
        :return: a list of integers
        """
        if isinstance(turnovers, (int, str, float)):
            turnovers = [turnovers]
        if not isinstance(turnovers, (list, tuple)):
            raise TypeError("Rotor turnover must be either a single integer/char, or a list/tuple of them, instead"
                            " got type: %s" % type(turnovers))

        ret = []

        for t in turnovers:
            if isinstance(t, float):
                if t - int(t) == 0:
                    t = int(t)
                else:
                    raise TypeError("Rotor turnovers must be integers or chars, got value: %f" % t)
            if isinstance(t, int):
                if t < 0 or t > 25:
                    raise ValueError("Rotor turnovers must be in the range [0, 25], got: %d" % t)
                ret.append(t)
            elif isinstance(t, str):
                if len(t) != 1:
                    raise ValueError("Rotor turnovers must be a single char, got: \"%s\"" % t)
                t = t.lower()
                v = ord(t) - ord('a')
                if v < 0 or v > 25:
                    raise ValueError("Rotor turnovers must be in the range ['A', 'Z'] or ['a', 'z'], got: '%s'" % t)
                ret.append(v)
            else:
                raise TypeError("Rotor turnovers must be either integers or chars, got type: %s" % type(t))
        return list(set(ret))

    @staticmethod
    def _check_position(position):
        """
        Checks whether or not the position is valid
        :param position: the position of the rotor
        :return: an integer
        """
        if isinstance(position, float):
            if position - int(position) == 0:
                position = int(position)
            else:
                raise TypeError("Rotor position must be an integer or char, got: %f" % position)
        if isinstance(position, int):
            if position < 0 or position > 25:
                raise ValueError("Rotor position must be in the range [0, 25], got: %d" % position)
            return position
        elif isinstance(position, str):
            if len(position) != 1:
                raise ValueError("Rotor position must be an integer or a single character, got the string: \"%s\""
                                 % position)
            position = position.lower()
            v = ord(position) - ord('a')
            if v < 0 or v > 25:
                raise ValueError("Rotor position must be in the range ['A', 'Z'] or ['a', 'z'], got: '%s'" % position)
            return v
        else:
            raise TypeError("Rotor position must be either an integer or character, got type: %s" % type(position))

    @staticmethod
    def _check_ring_setting(ring_setting):
        """
        Checks to make sure the ring_setting is valid. Just calls _check_position(), this is really only here in
            case in the future I need to check something else with it
        :param ring_setting: the ring setting to check
        :return: and integer
        """
        return Rotor._check_position(ring_setting)


class Reflector:
    def __init__(self, mapping):
        """
        A reflector plate
        :param mapping: a string / list of integers or chars of size 26, where the index refers to the incoming signal
            letter, and the value at that index refers to the outgoing reflected signal letter. Integers must be in the
            range [0, 25] and characters must be in the range ['A', 'Z'] or the lowercase ['a', 'z'].
            Importantly: values can not map to themselves
            Mapping must be a list containing each letter in the alphabet exactly once
        """
        self.mapping = Reflector._check_mapping(mapping)

    def reflect(self, val):
        """
        Returns the signal letter after reflecting the incoming signal letter val
        :param val: the incoming signal
        :return: the reflected signal
        """
        if not isinstance(val, int) or val < 0 or val > 25:
            raise ValueError("Got an erroneous val to reflect: %s" % val)
        return self.mapping[val]

    @staticmethod
    def _check_mapping(mapping):
        """
        Checks that the mapping is a valid mapping
        :param mapping: the mapping
        :return: a list of integers
        """
        if isinstance(mapping, str):
            mapping = [c for c in mapping]
        if not isinstance(mapping, (list, tuple)):
            raise TypeError("Reflector plate mapping must be a list/tuple, got type: %s" % type(mapping))
        if len(mapping) != 26:
            raise ValueError("Reflector plate mapping must be of size 26, instead got size: %d" % len(mapping))

        ret = []

        for i, m in enumerate(mapping):
            if isinstance(m, float):
                if m - int(m) == 0:
                    m = int(m)
                else:
                    raise TypeError("Reflector plate mappings must be integers or chars, got: %f" % m)
            if isinstance(m, int):
                if m < 0 or m > 25:
                    raise ValueError("Reflector plate mappings must be in the range [0, 25], got: %d" % m)
            elif isinstance(m, str):
                if len(m) != 1:
                    raise ValueError("Reflector plate mappings must be either integer or chars, got string: \"%s\"" % m)
                m = m.lower()
                v = ord(m) - ord('a')
                if v < 0 or v > 25:
                    raise ValueError("Reflector plate mappings must be in the range ['A', 'Z'] or ['a', 'z'], got: %s"
                                     % m)
                m = v
            else:
                raise TypeError("Reflector plate mappings must be an integer or char, instead got type: %s" % type(m))

            if i == m:
                raise ValueError("Values can not map to themselves. "
                                 "Reflector plate mapping at index: %d maps to the value: %d" % (i, m))
            ret.append(m)

        for i in range(26):
            if i not in ret:
                raise ValueError("Reflector plate mapping must contain each letter in the alphabet exactly once")

        return ret


ROTOR_1 = Rotor("EKMFLGDQVZNTOWYHXUSPAIBRCJ", "Q")
ROTOR_2 = Rotor("AJDKSIRUXBLHWTMCQGZNPYFVOE", "E")
ROTOR_3 = Rotor("BDFHJLCPRTXVZNYEIWGAKMUSQO", "V")
ROTOR_4 = Rotor("ESOVPZJAYQUIRHXLNFTGKDCMWB", "J")
ROTOR_5 = Rotor("VZBRGITYUPSDNHLXAWMJQOFECK", "Z")
ROTOR_6 = Rotor("JPGVOUMFYQBENHZRDKASXLICTW", ["Z", "M"])
ROTOR_7 = Rotor("NZJHGRCXMYSWBOUFAIVLPEKQDT", ["Z", "M"])
ROTOR_8 = Rotor("FKQHTLXOCBJSPDZRAMEWNIUYGV", ["Z", "M"])

REFLECTOR_BETA = Reflector("LEYJVCNIXWPBQMDRTAKZGFUHOS")
REFLECTOR_GAMMA = Reflector("FSOKANUERHMBTIYCWLQPZXVGJD")
REFLECTOR_A = Reflector("EJMZALYXVBWFCRQUONTSPIKHGD")
REFLECTOR_B = Reflector("YRUHQSLDPXNGOKMIEBFZCWVJAT")
REFLECTOR_C = Reflector("FVPJIAOYEDRZXWGCTKUQSBNMHL")
REFLECTOR_B_THIN = Reflector("ENKQAUYWJICOPBLMDXZVFTHRGS")
REFLECTOR_C_THIN = Reflector("RDOBJNTKVEHMLFCWZAXGYIPSUQ")
