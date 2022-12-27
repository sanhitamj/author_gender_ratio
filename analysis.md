# Analysis Notes

### How to determine gender of the authors.

1. Got the first names of the authors. Dropped titles like Dr, Prof, Ms etc.

2. Out of 30980 authors whose 'About' info was scraped, only 537 was empty. For
the rest of the authors, generally they had used third person in the 'About' section.
The code counted if masculine or feminine adjectives or titles were used more number
of times.

* Feminine adjectives/titles - she, her, hers, ms, mrs. miss
* Masculine adjectives/titles - he, him, his, mr., mr

  The logic used is -

  ``` pseudocode
  if num_fem_words > num_masc_words then female;
  if num_fem_words < num_masc_words then male;
  else NaN
  ```
  Such NaNs are dropped from the counting.

3. Mapped the names to the gender; some names are used for women and men. Also the
logic mentioned above will not always work correctly. So 87 names were found in both
genders. Some of those were clearly mislabeled in some cases. For example, Barbara, Peter
etc. In such cases, used majority voting to decide the gender of the author.

  One special name -

  Some of this is certainly wrong. For example, for the name Lane, majority voting suggested
  it to be a man's name. One of the Lanes is [Lane Rebelo](https://www.amazon.com/stores/author/B07CCKR9SP).
  From the image, looks like a woman. This can be further improved using the author's images,
  and training a model to label genders. What would the model do with one [Lane
    Hart](https://www.amazon.com/stores/author/B00J22NZTA) though?

  I have left such classification, assuming that the logic would make such counting errors
  almost equally on either sides.

### Analysis

1. In this way, I found 2316 unique names; out of those 1418 are women's names and
898 are men's names. Perhaps people get more creative about their girls' names and/or
I found more women with diverse backgrounds than men. Remember, I started with a
Nigerian and not-anglicised woman's name.

2. The gender ratio of the authors I found by scraping, for whom I have an Amazon URL,
their img_url, about info is almost equal; slight more percentage of women -

  | Gender | Percentage (rounded) | Counts |
  | ------ | -------------------- | ------ |
  |   1.0  |  0.52                |  4024  |
  |   0.0  |  0.48                |  3742  |

3. Now with the mapped authors dataframe. Each row has an author, and another author
mapped to her, or an author from her page. The pair is unique for each row. For 10996
unique authors, 203161 authors were found mapped to them; almost 18.5 mappings per
author.

4. Missing Labels - or missing gender information

  Out of 203161 rows, original author gender is labeled from 188635 rows (including
    multiple counting). For 762 unique names gender was not labeled. Some of these names
  obviously do not have genders; for example, Sterling Test Prep, Farlex International,
  Appearance Publishers. All those are removed from the further analysis.

  Gender labels are available for 165296 mapped authors (including multiple counting).
  The missing ones have 4899 unique names. Those rows are dropped when counting genders
  of mapped authors.

5. Mapped Authors' gender distribution -

  After removing Authors whose gender isn't labeled, the average mapped authors to women
  authors is 19.5; for men authors, the average is 17.3

  The genders of mapped authors is highly skewed to the authors' genders though.

  | Author's gender | Mapped Women (%) | Mapped Men (%) |
  | --------------- | ---------------  | ---------------|
  | Women           |    71.7          |   28.3         |
  | Men             |    27.4          |   72.6         |



### Conclusion

I am aware that people don't just follow in 2 neat genders. For this little project, along with
other assumptions, this assumption encompasses majority of the population, also makes the project
easy.

The Author data scraped shows no bias towards their own gender; that is women authors are recommended
more (71.7%) on a woman author's page; and men authors are equally more recommended on men author's
page (72.6%). So if one reads more books by women, they'd be shown more recommendations of women
authors.

With these data, I didn't see any pattern like the one described in The Authority Gap, quoted
[here](the_authority_gap.md).
