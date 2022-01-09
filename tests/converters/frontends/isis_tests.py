import os
import typing
import unittest

from mutwo.core import events
from mutwo.core import parameters

from mutwo.ext import converters


class NoteLikeWithText(events.basic.SimpleEvent):
    """NoteLike with additional consonants and vowel attributes.

    Mocking class (only for testing purposes).
    """

    def __init__(
        self,
        pitch_list,
        duration: parameters.abc.DurationType,
        volume,
        consonants: typing.Tuple[str],
        vowel: str,
    ):
        super().__init__(duration)
        self.pitch_list = pitch_list
        self.volume = parameters.volumes.DirectVolume(volume)
        self.consonants = consonants
        self.vowel = vowel


class IsisScoreConverterTest(unittest.TestCase):
    score_path = "tests/converters/frontends/isis-score"

    @classmethod
    def setUpClass(cls):
        cls.converter = converters.frontends.isis.IsisScoreConverter()

    @classmethod
    def tearDownClass(cls):
        # remove score files
        os.remove(cls.score_path)

    def test_convert_simple_event(self):
        simple_event = NoteLikeWithText(
            [parameters.pitches.WesternPitch()], 2, 0.5, ("t",), "a"
        )
        self.converter.convert(simple_event, self.score_path)

        expected_score = (
            "[lyrics]\nxsampa: {} {}\n\n[score]\nmidiNotes: {}\nglobalTransposition:"
            " 0\nrhythm: {}\nloud_accents: {}\ntempo: {}".format(
                simple_event.consonants[0],
                simple_event.vowel,
                simple_event.pitch_list[0].midi_pitch_number,
                simple_event.duration,
                simple_event.volume.amplitude,
                self.converter._tempo,
            )
        )

        with open(self.score_path, "r") as f:
            self.assertEqual(f.read(), expected_score)

    def test_convert_sequential_event(self):
        # Test if auto tie works!
        sequential_event = events.basic.SequentialEvent(
            [
                NoteLikeWithText(
                    [parameters.pitches.WesternPitch()], 2, 0.5, ("t",), "a"
                ),
                events.basic.SimpleEvent(4),
                NoteLikeWithText([], 3, 1, tuple([]), ""),
                NoteLikeWithText(
                    [parameters.pitches.WesternPitch()], 2, 0.5, ("t",), "a"
                ),
            ]
        )
        expected_score = (
            "[lyrics]\nxsampa: {0} {1}\n        _ {0} {1}\n\n[score]\nmidiNotes: {2},\n"
            "           0.0, {2}\nglobalTransposition: 0\nrhythm: {3},\n        7,"
            " {3}\nloud_accents: {4},\n              0, {4}\ntempo: {5}".format(
                sequential_event[0].consonants[0],
                sequential_event[0].vowel,
                sequential_event[0].pitch_list[0].midi_pitch_number,
                sequential_event[0].duration,
                sequential_event[0].volume.amplitude,
                self.converter._tempo,
            )
        )

        self.converter.convert(sequential_event, self.score_path)
        with open(self.score_path, "r") as f:
            self.assertEqual(f.read(), expected_score)

    def test_convert_rest(self):
        simple_event = events.basic.SimpleEvent(3)
        self.converter.convert(simple_event, self.score_path)

        expected_score = (
            "[lyrics]\nxsampa: _\n\n[score]\nmidiNotes: 0.0\nglobalTransposition:"
            " 0\nrhythm: {}\nloud_accents: 0\ntempo: {}".format(
                simple_event.duration,
                self.converter._tempo,
            )
        )

        with open(self.score_path, "r") as f:
            self.assertEqual(f.read(), expected_score)


if __name__ == "__main__":
    unittest.main()
