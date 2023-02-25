#!/usr/bin/env python3

import nanopi_timer

if __name__ == "__main__":

    nanopi = nanopi_timer.Nanopi_control()
    nanopi.check_network()
