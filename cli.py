import logging
from nlu import NLU
from graph import graph

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARN)

    print("Welcome to the NLU command line")
    print("Start typing statements and questions in Mentalase or English or help for available commands")

    print("")

    nlu = NLU()
    while True:

        command = input("> ")  # type: str
        if command == 'help':
            print("Input Mentalase statements or questions one line per expression, or")
            print("input free text statements or questions (multiple statements per line, questions separately), or")
            print("one of these commands:")
            print("  working_memory : graph description of working memory state")
            print("  question_store : graph description of last question store")
            print("  reset          : reset session")
            print("  log [level]    : set log level")
            print("  help           : this help")
            print("  exit           : exit")
        elif command == 'exit':
            break
        elif command == 'reset':
            nlu = NLU()
            print("Session reset")
        elif command == 'working_memory':
            print("\n%s\n" % graph(nlu.working_memory))
        elif command == 'question_store':
            print("\n%s\n" % graph(nlu.question_store))
        elif command.startswith("log "):
            level = command[4:].upper()
            print("Setting log level to [%s]" % level)
            try:
                logging.root.setLevel(level)
            except ValueError:
                print("Unknown value. Valid values: %s" % ", ".join(logging._nameToLevel))
        elif len(command) == 0:
            pass
        else:
            if "?" in command:
                # question
                try:
                    q, a, c = nlu.ask(command)
                    answer = nlu.create_answer(q, a)

                    print("Question %s" % q)
                    if a is None:
                        print("Answer: None")
                    else:
                        print("Answer: %s (p=%r)" % (answer, c.probability))
                except StopIteration:
                    print("Question not understood.")
            else:
                # statement
                understood = False
                for parsed in nlu.integrate(command):
                    understood = True
                    print("Statement: %s" % parsed)
                if not understood:
                    print("Statement not understood.")
