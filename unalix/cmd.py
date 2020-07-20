import argparse
import unalix

def cmd():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        '-u', '--url', type=str, help='url to be processed'
    )
    shell_options = argument_parser.parse_args()
    
    print(
		unalix.clear_url(shell_options.url)
	)
    
