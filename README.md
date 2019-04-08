```
    __    ____  __________ 
   / /   / __ \/_  __/ __ \
  / /   / / / / / / / / / /
 / /___/ /_/ / / / / /_/ / 
/_____/\____/ /_/  \____/ 
```
# Fun with lottery numbers

[![asciicast](https://asciinema.org/a/wtHBSKli33x9g5IgoX9M4ftdM.svg)](https://asciinema.org/a/wtHBSKli33x9g5IgoX9M4ftdM)

This repository is for a personal project, it is a collection of scripts I call "experiments" on lottery numbers (wrapped in a CLI). It is not a library. It hasn't made any correct prediction yet, which should not be a surprise :-) I hope some bits of code might be useful to some, I've had a hard time figuring out some stuff here myself. As always, simple things are not necessarily easy because [reality has a surprising amount of detail](http://johnsalvatier.org/blog/2017/reality-has-a-surprising-amount-of-detail)!

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installing](#installing)
- [Running the experiments](#running-the-experiments)
  - [First run](#first-run)
  - [X1 - Statistics with Dieharder & Ent](#x1-statistics-with-dieharder-ent)
  - [X2 - Plots with Matplotlib](#x2-plots-with-matplotlib)
  - [X3 - On-Line Encyclopedia of Integer Sequences](#x3-on-line-encyclopedia-of-integer-sequences)
  - [X4 - Predictions made with a Compact Prediction Tree +](#x4-predictions-made-with-a-compact-prediction-tree)
  - [X5 - Predictions made with the Prophet library (FB)](#x5-predictions-made-with-the-prophet-library-fb)
  - [X6 - Predictions made with different sources of randomness](#x6-predictions-made-with-different-sources-of-randomness)
- [Running the tests](#running-the-tests)
- [Deployment](#deployment)
- [Built With](#built-with)
- [Contributing](#contributing)
- [Author](#author)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

To have the full experience on your machine, you need:

- [Python](https://www.python.org/) 3.7 or higher.
- Copy this project's files where you want them:

    ```
    $ cd /to/where/you/want/the/loto/project
    $ git clone https://github.com/baychimo/loto
    ```

- To run the statistics, you will need: [dieharder](https://webhome.phy.duke.edu/~rgb/General/dieharder.php) and [ENT](https://www.fourmilab.ch/random/).

    On macOS, with [homebrew](https://brew.sh/):

    ```
    $ brew install dieharder ent
    ```

    On linux/ubuntu:

    ```
    $ apt install dieharder ent
    ```

- To get the predictions of a Compact Prediction Tree+ algorithm, you need to download and compile the [SPMF java library](http://www.philippe-fournier-viger.com/spmf/index.php?link=download.php). You need to have java installed and your JAVA path set correctly (JAVA_HOME). Try these instructions: [linux/ubuntu](https://www.digitalocean.com/community/tutorials/how-to-install-java-with-apt-on-ubuntu-18-04), [macOS](https://stackoverflow.com/questions/24342886/how-to-install-java-8-on-mac).

    This is my java environment (if it helps):
    ```
    $ echo $JAVA_HOME
    /Library/Java/JavaVirtualMachines/openjdk-12.jdk/Contents/Home
    
    $ which java && java --version
    /usr/bin/java
    openjdk 12 2019-03-19
    OpenJDK Runtime Environment (build 12+33)
    OpenJDK 64-Bit Server VM (build 12+33, mixed mode, sharing)
    
    $ which javac && javac --version
    /usr/bin/javac
    javac 12
    ```

    These instructions worked for me:
    ```
    $ cd /to/where/you/downloaded/the/lib
    $ unzip -q spmf.zip
    
    $ cd /to/where/you/downloaded/the/lib/ca
    $ javac -encoding ISO-8859-1 -d ./build $(find . -name "*.java")
    $ cd build
    $ jar cvf spmf.jar *
    
    $ mv spmf.jar /to/where/you/want/the/loto/project/loto/loto/lib
    ```

These instructions are for macOS and Linux. Everything should run on Windows as well.

> Note: the project was developed on macOS. Matplotlib needs a [venv](https://docs.python.org/3/library/venv.html), not a [virtualenv](https://virtualenv.pypa.io/en/stable/) or it crashes instead of generating plots. Pipenv is not to be used here if you're on macOS (because it exclusively uses virtualenv), or things will break.

Then you copy this project's files where you want them:

```
$ cd /to/where/you/want/the/loto/project
$ git clone https://github.com/baychimo/loto
```
If you don't have [git](https://git-scm.com/downloads) installed, you can download the files by clicking the green "Clone or download" button at the top of the page.

### Installing

Create a virtual environment on your machine with, for instance:

```
$ python3 -m venv ~/.virtualenvs/loto
```

If it's not done already, copy this project's files where you want them:

```
$ cd /to/where/you/want/the/loto/project
$ git clone https://github.com/baychimo/loto
```

Activate the environment and install the needed python packages:

```
$ source ~/.virtualenvs/loto/bin/activate && cd /to/where/you/want/the/loto/project
(loto)$ pip install --upgrade pip setuptools
```

If you simply want to run the experiments:

```
(loto)$ pip install -r requirements_prod.txt
```

It might take a while, some packages are heavy/long to install (pystan/fbprophet in particular).
If you also want to be able to run the tests, install dev packages:

```
(loto)$ pip install -r requirements_dev.txt
```

## Running the experiments

[![Experiments: composite of terminal screenshots](https://raw.githubusercontent.com/baychimo/loto/screenshots/composites/screenshots_sm.png "Experiments: composite of terminal screenshots")](https://raw.githubusercontent.com/baychimo/loto/screenshots/composites/screenshots_lg.png)

### First run

Whatever experiment you want to run first, you need to download and create a database of draw numbers, otherwise nothing will work. This is done either via the `-r` option accompanied by a command (i.e. an experiment code 'x2'), or via the `rf` command, as shown on the help screen:

```
(loto)$ python loto/core.py --help
Usage: core.py [OPTIONS] COMMAND [ARGS]...

  Command line interface to run experiments (stats and predictions) on
  lottery numbers

  Have fun!

Options:
  -r, --refresh  Refresh database before running experiment
  --help         Show this message and exit.

Commands:
  rf  Refresh/create DB only
  x1  Statistics with Dieharder & Ent
  x2  Plots with Matplotlib
  x3  Checking "previous art" from OEIS (On-Line Encyclopedia of Integer...
  x4  Predictions made with a Compact Prediction Tree + (SPMF/Java)
  x5  Predictions made with the Prophet library (FB)
  x6  Predictions made with different sources of randomness 
```

So for instance, we might start with experiment n°4 which we will prepend with the `-r` option:

```
(loto)$ python loto/core.py -r x4
```

This will download the lottery numbers, create a database, and run the x4 experiment.
Or you can simply start by creating the database without running an experiment, with the `rf` command:

```
(loto)$ python loto/core.py rf
```

And that's it, you're set! From now on you will only need to remember to refresh the database from time to time, every Wednesday and Saturday after each bi-weekly draw for example.

### X1 - Statistics with Dieharder & Ent

Ent is very fast, but according to some people on the internet is not very reliable anymore. But we're here to have fun, right. Dieharder is very long to run, so I'd advise to run it once to see what it does and unless you poke a hole in Euromillions' randomness, it's not worth running again. If you read the source, you'll find a simple example usage of the subprocess module.

Run the experiment like so:

```
(loto)$ python loto/core.py x1
   _  _____   _____ __        __  _      __  _          
  | |/ <  /  / ___// /_____ _/ /_(_)____/ /_(_)_________
  |   // /   \__ \/ __/ __ `/ __/ / ___/ __/ / ___/ ___/
 /   |/ /   ___/ / /_/ /_/ / /_/ (__  ) /_/ / /__(__  ) 
/_/|_/_/   /____/\__/\__,_/\__/_/____/\__/_/\___/____/  
                                                        

Ent is installed and in path

Dieharder is installed and in path

[...Long output...]
```

### X2 - Plots with Matplotlib

Here's a composite of the four plots produced by this experiment:

[![Plots: composite of plots generated in x2](https://raw.githubusercontent.com/baychimo/loto/screenshots/composites/x2_plots_sm.png "Plots: composite of plots generated in x2")](https://raw.githubusercontent.com/baychimo/loto/screenshots/composites/x2_plots_lg.png)

Run the experiment like so:

```
(loto)$ python loto/core.py x2
   _  _____      ____  __      __      
  | |/ /__ \    / __ \/ /___  / /______
  |   /__/ /   / /_/ / / __ \/ __/ ___/
 /   |/ __/   / ____/ / /_/ / /_(__  ) 
/_/|_/____/  /_/   /_/\____/\__/____/  
                                       

Heatmap created    ::   x2_heatmap.png                                          
Line plot created  ::   x2_line.png                                             
Area plot created  ::   x2_area.png                                             
Pie plot created   ::   x2_pie.png                                              
100%|█████████████████████████████████████████████| 4/4 [00:07<00:00,  1.83s/it]

All images were saved to this folder:
/to/where/you/want/the/loto/project/data/images/
```

Most graphs generated here are trying to be visually pleasing if not very helpful for guessing the next winning numbers. The plots will be saved in the data/images folder.

### X3 - On-Line Encyclopedia of Integer Sequences

Here we are looking for prior art: is there a sequence that has already been cited or added to The On-Line Encyclopedia of Integer Sequences? Is there an existing and known pattern here, or a statistical coincidence?

Run the experiment like so:

```
(loto)$ python loto/core.py x3
   _  _______    ____    ______   ____  _____
  | |/ /__  /   / __ \  / ____/  /  _/ / ___/
  |   / /_ <   / / / / / __/     / /   \__ \ 
 /   |___/ /  / /_/ / / /___ _ _/ / _ ___/ / 
/_/|_/____/   \____(_)_____/(_)___/(_)____/  
                                             

No luck for query       : https://oeis.org/search?fmt=json&q=16,10,46,39,6,8,11
No luck for query       : https://oeis.org/search?fmt=json&q=40,17,24,19,18,8,4
No luck for query       : https://oeis.org/search?fmt=json&q=5,13,7,19,31,9,2
No luck for query       : https://oeis.org/search?fmt=json&q=46,24,42,15,3,12,9
No luck for query       : https://oeis.org/search?fmt=json&q=9,6,1,47,34,12,7
No luck for query       : https://oeis.org/search?fmt=json&q=17,43,26,4,30,11,6
No luck for query       : https://oeis.org/search?fmt=json&q=47,43,19,23,12,2,6
No luck for query       : https://oeis.org/search?fmt=json&q=13,23,26,47,32,6,10
No luck for query       : https://oeis.org/search?fmt=json&q=9,26,16,2,36,6,7
No luck for query       : https://oeis.org/search?fmt=json&q=7,45,10,1,29,5,3
```

If it ever shows "Results found for query", instead of "No luck for query", you're invited to manually go to the [OEIS website](https://oeis.org/) with the lucky URL and check which sequence it has been found in. It is highly unlikely, but my instincts could be wrong hence this little script :-)

### X4 - Predictions made with a Compact Prediction Tree +

As with other ideas in this project, we're stabbing in the dark with inappropriate tools to see if we get lucky. Here we are trying to load the lottery numbers in a compact prediction tree + and get predictions out of it (link to the paper can be found on the documentation page of the [CPT+ algorithm](http://www.philippe-fournier-viger.com/spmf/CPTPlus.php) of the SPMF library)

```
(loto)$ python loto/core.py x4
   _  ____ __     ______                                 __ 
  | |/ / // /    / ____/___  ____ ___  ____  ____ ______/ /_
  |   / // /_   / /   / __ \/ __ `__ \/ __ \/ __ `/ ___/ __/
 /   /__  __/  / /___/ /_/ / / / / / / /_/ / /_/ / /__/ /_  
/_/|_| /_/     \____/\____/_/ /_/ /_/ .___/\__,_/\___/\__/  
                                   /_/                      
    ____                ___      __  _                ______             
   / __ \________  ____/ (_)____/ /_(_)___  ____     /_  __/_______  ___ 
  / /_/ / ___/ _ \/ __  / / ___/ __/ / __ \/ __ \     / / / ___/ _ \/ _ \
 / ____/ /  /  __/ /_/ / / /__/ /_/ / /_/ / / / /    / / / /  /  __/  __/
/_/   /_/   \___/\__,_/_/\___/\__/_/\____/_/ /_/    /_/ /_/   \___/\___/ 
                                                                         
       
    __ 
 __/ /_
/_  __/
 /_/   
       

100%|███████████████████████████████████████████| 14/14 [00:00<00:00, 27.75it/s]

================================================================================
| C O M P A C T   P R E D I C T I O N   T R E E  +                             |
--------------------------------------------------------------------------------
| Numbers for draw (-2)          :      | 02 | 09 | 16 | 26 | 36 |   | 06 | 07 |
--------------------------------------------------------------------------------
| Prediction for draw (-1)       :      | 04 | 05 | 14 | 21 | 39 |   | 02 | 03 |
--------------------------------------------------------------------------------
| Actual numbers for draw (-1)   :      | 01 | 07 | 10 | 29 | 45 |   | 03 | 05 |
--------------------------------------------------------------------------------
| Prediction for next draw       :      | 05 | 15 | 17 | 38 | 44 |   | 02 | 08 |
================================================================================

JVM has been shutdown
```

Sometimes the CPT+ might not be able to produce a prediction, so you'll see a '00' where it fell short. When this happens to me, I go check what experiment n°6 gives me (x6) to fill in the blanks.

### X5 - Predictions made with the Prophet library (FB)

Another tool twisted out of its main function to help us have fun. The predictions here are unusable (so far), but at least nice plots are generated:

[![Prophet plots: composite of plots generated in x5](https://raw.githubusercontent.com/baychimo/loto/screenshots/composites/x5_plots_sm.png "Prophet plots: composite of plots generated in x5")](https://raw.githubusercontent.com/baychimo/loto/screenshots/composites/x5_plots_lg.png)

```
(loto)$ python loto/core.py x5
   _  __ ______   ____                   __         __ 
  | |/ // ____/  / __ \_________  ____  / /_  ___  / /_
  |   //___ \   / /_/ / ___/ __ \/ __ \/ __ \/ _ \/ __/
 /   |____/ /  / ____/ /  / /_/ / /_/ / / / /  __/ /_  
/_/|_/_____/  /_/   /_/   \____/ .___/_/ /_/\___/\__/  
                              /_/                      

ball_1                                                            0:00:08.318668
Image generated: x5_prophecy_ball_1.png                                         
Here: /Users/jonathan/Projects/loto/loto/data/images/
ball_2                                                            0:00:07.980091
Image generated: x5_prophecy_ball_2.png                                         
Here: /Users/jonathan/Projects/loto/loto/data/images/
ball_3                                                            0:00:08.039566
Image generated: x5_prophecy_ball_3.png                                         
Here: /Users/jonathan/Projects/loto/loto/data/images/
ball_4                                                            0:00:08.172079
Image generated: x5_prophecy_ball_4.png                                         
Here: /Users/jonathan/Projects/loto/loto/data/images/
ball_5                                                            0:00:08.035069
Image generated: x5_prophecy_ball_5.png                                         
Here: /Users/jonathan/Projects/loto/loto/data/images/
star_1                                                            0:00:08.001823
Image generated: x5_prophecy_star_1.png                                         
Here: /Users/jonathan/Projects/loto/loto/data/images/
star_2                                                            0:00:07.946917
Image generated: x5_prophecy_star_2.png                                         
Here: /Users/jonathan/Projects/loto/loto/data/images/
100%|█████████████████████████████████████████████| 7/7 [00:59<00:00,  8.50s/it]

================================================================================
| P R O P H E T                                                                |
--------------------------------------------------------------------------------
| Numbers for draw (-2)          :      | 09 | 26 | 16 | 02 | 36 |   | 06 | 07 |
--------------------------------------------------------------------------------
| Prediction for draw (-1)       :      | 28 | 28 | 28 | 25 | 23 |   | 07 | 07 |
--------------------------------------------------------------------------------
| Actual numbers for draw (-1)   :      | 07 | 45 | 10 | 01 | 29 |   | 05 | 03 |
--------------------------------------------------------------------------------
| Prediction for next draw       :      | 27 | 28 | 28 | 24 | 25 |   | 07 | 07 |
================================================================================
```

### X6 - Predictions made with different sources of randomness

Here we make random predictions using four different sources of entropy: dev/urandom, random.org, NIST randomness beacon and ANU's quantum RNG. We're hopelessely trying to query the randomness sources simultaneously via the multiprocessing module.

```
   _  _______    ____                  __              
  | |/ / ___/   / __ \____ _____  ____/ /___  ____ ___ 
  |   / __ \   / /_/ / __ `/ __ \/ __  / __ \/ __ `__ \
 /   / /_/ /  / _, _/ /_/ / / / / /_/ / /_/ / / / / / /
/_/|_\____/  /_/ |_|\__,_/_/ /_/\__,_/\____/_/ /_/ /_/ 
                                                       

Getting entropy from NIST beacon...
Getting random sequences from random.org...
Getting entropy from ANU's Quantum RNG...

================================================================================
| R A N D O M   P R E D I C T I O N S                                          |
--------------------------------------------------------------------------------
| NIST Beacon                    :      | 06 | 12 | 14 | 22 | 41 |   | 07 | 12 |
--------------------------------------------------------------------------------
| Random.org                     :      | 15 | 27 | 38 | 42 | 46 |   | 03 | 04 |
--------------------------------------------------------------------------------
| ANU Quantum RNG                :      | 05 | 07 | 31 | 42 | 49 |   | 08 | 12 |
--------------------------------------------------------------------------------
| OS random (dev/urandom)        :      | 02 | 14 | 30 | 33 | 45 |   | 02 | 04 |
================================================================================
```

If any of the sources is unavailable, the corresponding prediction is filled with zeros.

## Running the tests

If you wish to run the unit tests for this project, just run this from the root of the project:

```
(loto)$ pytest -v --durations=0 --hypothesis-show-statistics tests/
```

It can seem quite slow given the number of tests, since [hypothesis](https://hypothesis.works/) runs multiple tests for each test (it's its job).

## Deployment

You could run this on a server of course and access it via ssh for example, or build a web UI to replace the old-school CLI, or create a prediction API on top of it, or etc. But it is beyond the scope of these instructions.

## Built With

Small project built atop the shoulders of giants. Viva open source! 
- [Pandas](https://pandas.pydata.org/) - Powerful dataframes, great for working with csv and sqlite3.
- [Prophet](https://facebook.github.io/prophet/) - Facebook's forecasting library. Used to forecast lottery numbers in x5.
- [Matplotlib](https://matplotlib.org/) - Plotting library used directly (see x2) or via prophet (see x5). Nice results.
- [Jpype](https://jpype.readthedocs.io/) - Python/Java interface, very useful once you "get it".
- [SPMF](http://www.philippe-fournier-viger.com/spmf/) - Open-source data mining mining library written in Java. Used here because it has an implementation of the [Compact Prediction Tree+ algorithm](http://www.philippe-fournier-viger.com/spmf/CPTPlus.php) (see x4).
- [Click](https://github.com/pallets/click) - Python composable command line interface toolkit. Wonderful tool to help create CLI quickly and simply.
- [Pyfiglet](https://github.com/pwaller/pyfiglet) - For the beautiful retro figlets :-)
- [Colorama](https://github.com/tartley/colorama) - For the beautiful retro colors :-)

## Contributing

I don't intend to maintain this project unless I have some new ideas that would make the process fun. It's one of those never-ending projects with no real scope where you can always add stuff, and always rewrite and improve what's already been done. So it has to be stopped somewhere.

Here are a few ideas for eventual forkers about what could be done:
- History: store every prediction so it can be compared with future draws.
- Make the refresh/create database option a little smarter: if the current day is a Wednesday or a Saturday, prompt the user to ask her if she wishes to refresh the data. Plus maybe make the option a command also.
- CLI: find out why click [setuptools integration](https://click.palletsprojects.com/en/7.x/setuptools/) does not work with [lazy imports](https://bugs.python.org/msg214954)(core.py).
- improvements:
    - x1: more statistical suites could be added, e.g. [PractRand](http://pracrand.sourceforge.net/) & [TestU01](http://simul.iro.umontreal.ca/testu01/tu01.html).
    - x1: an option could be added to not run every test suite, dieharder can be very long for instance.
    - x2: maybe something interactive, or more modern than matplotlib?
    - x3: this script can definitely be improved (this is always true right, but here especially).
    - x5: find a way to make the results useful, as in: a usable prediction.

If you have any questions, need further instructions for your platform, do not hesitate to open an issue. And feel free to fork it of course! That's why it's here for. Have fun!

## Author

**Jonathan Guitton** - [Baychimo](https://github.com/baychimo).

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

- Tools and services used
    - [Dieharder](https://webhome.phy.duke.edu/~rgb/General/dieharder.php) - "New" and enhanced version of the diehard test suite, containing [NIST's STS](https://csrc.nist.gov/projects/random-bit-generation/documentation-and-software/guide-to-the-statistical-tests) as well. Used in x1.
    - [ENT](https://www.fourmilab.ch/random/) - A pseudorandom number sequence test program. Used in x1.
    - [NIST Beacon](https://www.nist.gov/programs-projects/nist-randomness-beacon) - NIST randomness beacon. Called in x6.
    - [Random.org](https://www.random.org/) - True random number service. Called in x6.
    - [ANU Quantum RNG](http://qrng.anu.edu.au/index.php) - The Australian National University's Quantum Random Numbers Service. Called in x6.
    - [OEIS](https://oeis.org/) - The On-Line Encyclopedia of Integer Sequences. Called in x3.
    - [Française des jeux](https://www.fdj.fr/) - Where we get the lottery numbers from in convenient csv format.
- Inspiration
    - [What is not random?](https://www.youtube.com/watch?v=sMb00lz-IfE) by Veritasium.
    - The [gambler's fallacy](https://en.wikipedia.org/wiki/Gambler's_fallacy) and the [law of averages](https://en.wikipedia.org/wiki/Law_of_averages).
    - [Joan R. Ginther](https://en.wikipedia.org/wiki/Joan_R._Ginther).
