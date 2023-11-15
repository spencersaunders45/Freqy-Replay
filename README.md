![An old radio in a pixel art style](img/pixel-radio-96.png)

# Freqy-Replay

## Getting started
If you already have UHD installed then do not run the `setup.py` script. It will
most likely mess things up. Just modify the code to point to where UHD is
installed on your system.

If UHD is not installed run `sudo setup.py` and then restart your computer.
There may be some extra debugging that will need to be done to get UHD working,
but it depends on your system.

## Using the application

### Monitor for packets
In the path `freqy-replay/python/` run the command `python3 replay.py m`. This
will start up the application in monitor mode and will begin scanning for packets.

If you are not sure what your settings should be you can go into the `config.toml`
file and under the [MONITOR] section change `view_sample` to true and change
samples_to_collect to get a larger or smaller sample of that frequency activity.
Once `view_sample` is enabled you can run `python3 replay.py m` and after a few
seconds you will get a plot showing you the airwave activity during that period.
This is helpful in identifying if there is any activity and at what level to 
set your threshold.

### Examining captured packets
It might be helpful to see what data was captured so you can find out what was
a packet and may be a false positive. To view all captured packets in a file use
`python3 replay.py n -m`. This will print out all the datasets as well as some 
metadata on that captured packet.

You can also filter what packets are shown by going into the `config.toml file`
and editing the [FILTER] section. This will filter out any datasets/packets that
do not match any of these filters. After you've added your filter parameters
you can run the same command again and you will see the non-filtered datasets
displayed.

### Attack mode
In the `config.toml` file specify what file and dataset you want to use for the
replay attack under the [ATTACK] portion of the file. To run the replay attack
use the command `python3 replay.py a`. This will being playing the packet over
and over again.