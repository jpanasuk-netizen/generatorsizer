"""Leo answers the desk without inventing another seat's words."""

import unittest

from leo.desk import handle
from leo.service import process_new
from leo.session import Session
from leo.bus import MemoryBus


class DeskTests(unittest.TestCase):
    def test_send_keeps_the_note_and_does_not_invent_a_reply(self):
        session = Session()
        result = handle(session, 'send gemini a message, say "hi" and ask him to send one back')
        self.assertEqual(len(result.actions), 1)
        self.assertEqual(result.actions[0].to, "gemini-spark")
        self.assertEqual(result.actions[0].text, "hi and ask him to send one back")
        self.assertIn("No reply yet", result.reply)
        self.assertNotIn("What's up", result.reply)
        self.assertNotIn("out of credit", result.reply.lower())

    def test_follow_up_remembers_the_open_note(self):
        session = Session()
        handle(session, 'send gemini a message, say "hi" and ask him to send one back')
        result = handle(session, "ok did they respond?")
        self.assertEqual(result.actions, [])
        self.assertIn("No reply from Gemini Spark yet", result.reply)
        self.assertNotIn("new conversation", result.reply.lower())
        self.assertIn("hi", result.reply)

    def test_reports_a_reply_only_after_it_is_recorded(self):
        session = Session()
        handle(session, "tell gemini to figure out where I put my keys")
        session.note_reply("gemini-spark", "Check the desk drawer.")
        result = handle(session, "did they respond?")
        self.assertEqual(result.reply, "Gemini Spark replied: Check the desk drawer.")

    def test_seat_name_alone_is_not_an_encyclopedia_entry(self):
        session = Session()
        result = handle(session, "gemini")
        self.assertEqual(result.actions, [])
        self.assertIn("note", result.reply.lower())
        self.assertNotIn("Bard", result.reply)

    def test_second_note_is_a_new_dispatch(self):
        session = Session()
        handle(session, "send gemini a message, say hi")
        result = handle(session, "send gemini another message who won the cubs game last night?")
        self.assertEqual(result.actions[0].to, "gemini-spark")
        self.assertEqual(result.actions[0].text, "who won the cubs game last night?")
        self.assertNotRegex(result.reply, r"\d+\s*-\s*\d+")

    def test_external_spend_and_publish_stop(self):
        for text in ("spend $50 on ads", "post it on twitter", "send an email to the client"):
            result = handle(Session(), text)
            self.assertEqual(result.gate, "jeremy-yes", text)
            self.assertEqual(result.actions, [], text)
            self.assertIn("Jeremy", result.reply)

    def test_ping_and_note_forms(self):
        ping = handle(Session(), "ping mimo")
        self.assertEqual(ping.actions[0].to, "mimo")
        self.assertEqual(ping.actions[0].text, "ping")
        note = handle(Session(), "send a note to gemini asking it to figure out when the cubs play next")
        self.assertEqual(note.actions[0].to, "gemini-spark")
        self.assertIn("cubs play next", note.actions[0].text)

    def test_thread_does_not_reset(self):
        session = Session()
        handle(session, "hey")
        handle(session, "send gemini a message, say hi")
        result = handle(session, "what did I just send?")
        self.assertIn("hi", result.reply)
        self.assertGreaterEqual(len(session.turns), 4)


class ServiceTests(unittest.TestCase):
    def test_bus_round_trip_posts_the_note_and_forwards_the_real_reply(self):
        bus = MemoryBus()
        bus.send(from_="desk", to="leo", text="send gemini a message, say hi", topic="talk")
        state = {"since": 0, "sessions": {}}
        first = process_new(bus, state)
        self.assertTrue(any("No reply yet" in line for line in first))
        handoff = [row for row in bus.messages if row["to"] == "gemini-spark"]
        self.assertEqual(len(handoff), 1)
        self.assertEqual(handoff[0]["from"], "Leo-Bot")
        self.assertNotIn("What's up", handoff[0]["text"])

        bus.send(from_="gemini", to="desk", text="hi back", topic="talk")
        second = process_new(bus, state)
        self.assertIn("Gemini Spark replied: hi back", second)
        again = process_new(bus, state)
        self.assertEqual(again, [])

    def test_ignores_its_own_posts(self):
        bus = MemoryBus()
        bus.send(from_="Leo-Bot", to="desk", text="already said", topic="talk")
        state = {"since": 0, "sessions": {}}
        self.assertEqual(process_new(bus, state), [])


if __name__ == "__main__":
    unittest.main()
