import argparse
import unalix

argument_parser = argparse.ArgumentParser()
argument_parser.add_argument(
	'-u', '--url', type=str, help='url to be processed'
)
shell_options = argument_parser.parse_args()

if __name__ == '__main__' and shell_options.url != None:
    print(
		unalix.clear_url(shell_options.url)
	)
