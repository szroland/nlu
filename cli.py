from nlu import NLU
from graph import graph


if __name__ == '__main__':

    print("Welcome to the NLU command line")
    print("Start typing statements and questions in Mentalase or help for available commands")

    print("")

    nlu = NLU()
    while True:

        command = input("> ")
        if command == 'help':
            print("Input Mentalase statements or questions one line per expression, or")
            print("  working_memory : graph description of working memory state")
            print("  question_store : graph description of last question store")
            print("  reset          : reset session")
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
        else:
            if "?" in command:
                # question
                q, a, c = nlu.ask(command)
                answer = nlu.create_answer(q, a)

                print("Question %s" % q)
                if a is None:
                    print("Answer: None")
                else:
                    print("Answer: %s (p=%r)" % (answer, c.probability))
            else:
                # statement
                parsed = nlu.integrate(command)
                print("Statement: %s" % parsed)
