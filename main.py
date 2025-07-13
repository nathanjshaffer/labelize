#!/usr/bin/env python3
from labelizer.run import run
import importlib.resources as resources



def package():
    with resources.path('my_package', 'data') as data_path:
        print(data_path)
    run()


def main():
    run()
    print('This is main')


if __name__ == '__main__':
    main()
