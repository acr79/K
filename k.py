"""K CLI — main entrypoint."""

import argparse
import sys
from core import bootstrap
from core.profile import print_profile_summary


def cmd_init(args):
    bootstrap()
    print("Run 'python k.py interview' to start your onboarding session.")


def cmd_interview(args):
    bootstrap()
    from interview import InterviewConductor
    conductor = InterviewConductor()
    conductor.run(resume=not args.fresh)


def cmd_chat(args):
    bootstrap()
    from agent import KAgent
    k = KAgent(voice_mode=False)

    print("\nK is ready. Type 'exit' to quit, 'reset' to clear conversation history.\n")

    while True:
        try:
            query = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not query:
            continue
        if query.lower() == "exit":
            break
        if query.lower() == "reset":
            k.reset_history()
            print("Conversation cleared.\n")
            continue

        print("K: ", end="")
        k.ask(query)
        print()


def cmd_voice(args):
    bootstrap()
    from agent import KAgent
    from voice import listen, speak

    k = KAgent(voice_mode=True)
    print("\nK voice mode — speak after 'Listening...'. Say 'goodbye' to exit.\n")

    while True:
        text = listen(timeout=8)
        if not text:
            continue

        print(f"You: {text}")

        if "goodbye" in text.lower() or "exit" in text.lower():
            speak("Goodbye.")
            break

        print("K: ", end="", flush=True)
        response = k.ask(text)
        print(response)
        speak(response)


def cmd_import(args):
    bootstrap()
    if args.type == "guns":
        from inventory import import_guns_csv
        import_guns_csv(args.file, dry_run=args.dry_run)
    else:
        print(f"Unknown import type: {args.type}")
        print("Available: guns")


def cmd_profile(args):
    bootstrap()
    print_profile_summary()


def cmd_research(args):
    bootstrap()
    from agent.tools import Researcher
    researcher = Researcher()
    researcher.run(args.query)


def main():
    parser = argparse.ArgumentParser(prog="k", description="K — Kenny's personal AI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init", help="Initialize K's databases")

    iv = sub.add_parser("interview", help="Run onboarding interview")
    iv.add_argument("--fresh", action="store_true", help="Start from scratch")

    sub.add_parser("chat", help="Text chat with K")
    sub.add_parser("voice", help="Voice mode")
    sub.add_parser("profile", help="Show current profile summary")

    res = sub.add_parser("research", help="Research a topic with live web data")
    res.add_argument("query", help="What to research (quote the full query)")

    imp = sub.add_parser("import", help="Import inventory data")
    imp.add_argument("type", choices=["guns"], help="Data type to import")
    imp.add_argument("file", help="Path to CSV file")
    imp.add_argument("--dry-run", action="store_true", help="Preview without writing")

    args = parser.parse_args()

    if args.command == "research":    cmd_research(args)
    elif args.command == "init":      cmd_init(args)
    elif args.command == "interview": cmd_interview(args)
    elif args.command == "chat":      cmd_chat(args)
    elif args.command == "voice":     cmd_voice(args)
    elif args.command == "import":    cmd_import(args)
    elif args.command == "profile":   cmd_profile(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
