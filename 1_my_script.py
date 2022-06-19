import sys

print('I am a python script')

if len(sys.argv) > 1:
    print(f'You have entered {sys.argv[1:]}')
