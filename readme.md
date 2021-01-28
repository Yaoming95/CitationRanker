
# Conference Citation Ranker
This code helps to retrieve all papers from conferences and rank them by the number of (Google Scholar) citations.

It will save the retrieved paper information to a .csv file containing the Title, Number of Citations, Web Link, Conference, 
and Year. The .csv file is sorted according to the Citation number.

This tool can help find the most cited papers in a conference and discover hot research topics.



## Requirements

Python3

[Chrome Diver](http://chromedriver.chromium.org/)

### Installation
1. Download Git Repo `git clone https://github.com/Yaoming95/CitationRanker.git`

2. Install requirements `pip install -r requirements.txt`

3. Download [Chrome Diver](http://chromedriver.chromium.org/) in order to enter Captcha when Google robot checking is enabled. After downloading chromedriver, rename it to chromedriver and put it into current folder.

4. Run the command (e.g., `python citationRanker.py -c <confence abbr> -y <year>`).

## Usage

General Usage
```bash 
python citationRanker.py -c <conference abbr> -y <year_start> \
 -e <year_end, optional> -o <output_path, optional> -kw <keywords, optional> \
 --driver <path for Chrome Driver, optional>
```

The code support multiple conferences and keyword, which shall be separated by comma 

The conference abbr. is case insensitive, but shall be consist with [dblp](https://dblp.org/).
For example, for [Conference on Neural Information Processing Systems](https://dblp.org/db/conf/nips/index.html),
`nips` is for papers before year 2017, and `neurips` is for ones after year 2018.

To get help
```bash
python citationRanker.py -h
```

### Simple Tutorial and Examples

1.Retrieve the publication of a single conference in a certain year
```bash
python citationRanker.py -c <conference> -y <year>

# e.g. If you want to retrieve the publications of SIGIR’18
python citationRanker.py -c sigir -y 2018
```

2.Retrieve the publication of multiple conferences in a certain year

```bash
python citationRanker.py -c <conference1>,<conference2>  -y <year>

# e.g. If you want to retrieve the publications of SIGIR’18 and KDD'18
python citationRanker.py -c sigir,kdd -y 2018
```

3.Retrieve the publication of a conferences in several years span.

```bash
python citationRanker.py -c <conference>  -y <start year> -e <end year>

# e.g. If you want to retrieve the publications of SIGIR from 2018 to 2020 
python citationRanker.py -c sigir -y 2018 -e 2020

# e.g. If you want to retrieve the publications of NIPS from 2017 to 2020
python citationRanker.py -c nips,neurips -y 2017 -e 2020
```

4.Retrieve the publications with keywords.

```bash
python citationRanker.py -c <conference>  -y <start year> -kw <keyword>

# e.g. If you want to retrieve the publications of SIGIR'18 about `search`
python citationRanker.py -c sigir -y 2018 -kw search

# e.g. If you want to retrieve the publications of EMNLP&ACL&NAACL about `machine translation` in 2019
python citationRanker.py -c emnlp,acl,naacl -y 2019 -kw machine,translation
```

5.Specify the output file

```bash
python citationRanker.py -c <conference> -y <year> -o <output file>

# e.g. If you want to retrieve the publications about search of SIGIR’18 and save it to search.csv
python citationRanker.py -c sigir -y 2018 -kw search -o search.csv
```

### About Captcha 
Sometimes you may encounter the following sentence in the terminal:

`Solve captcha manually and press enter here to continue...`

No worries, this is caused by Google's robot detection.
Please complete the Captcha in the pops-up Chrome window, 
and then press Enter in the terminal. Please do not close the pop-up window when you finish the Captcha.





## Acknowledgment

WittmannF's [repo](https://github.com/WittmannF/sort-google-scholar) helped my development.