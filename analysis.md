# Analysis

## How to determine gender of the authors.

1. Got the first names of the authors. Dropped titles like Dr, Prof, Ms etc.

2. Out of 30980 authors whose 'About' info was scraped, only 537 was empty. For
the rest of the authors, generally they had used third person in the 'About' section.
The code counted if masculine or feminine adjectives or titles were used more number
of times.

* Feminine adjectives/titles - she, her, hers, ms, mrs. miss
* Masculine adjectives/titles - he, him, his, mr., mr

The logic used is -

If num_fem_words > num_masc_words then female;
if num_fem_words < num_masc_words then male;
else NaN.

Such NaNs are dropped from the counting.

3. Mapped the names to the gender; some names are used for women and men. Also the
logic mentioned above will not always work correctly. So 87 names were found in both
genders. Some of those were clearly mislabeled in some cases. For example, Barbara, Peter
etc. In such cases, used majority voting to decide the gender of the author.

One special name -

Some of this is certainly wrong. For example, for the name Lane, majority voting suggested
it to be a man's name. One of the Lanes is [Lane Rebelo](https://www.amazon.com/stores//Lane-Rebelo/e/B07CCKR9SP). From the image, looks like a woman. This can be further improved using the author's images,
and training a model to label genders. What would the model do with one [Lane
  Hart](https://m.media-amazon.com//Lane-Hart/e/B00J22NZTA) though?

I have left such classification, assuming that the logic would make such counting errors
almost equally on either sides.

4. In this way, I found 2316 unique names; out of those 1418 are women's names and
898 are men's names. Perhaps people get more creative about their girls' names and/or
I found more women with diverse backgrounds than men. Remember, I started with a
Nigerian and not-anglicised woman's name.

5. The gender ratio of the authors I found by scraping, for whom I have an Amazon URL,
their img_url, about info is almost equal; slight more percentage of women -

| Gender | Percentage (rounded) | Counts |
| ------ | -------------------- | ------ |
|   1.0  |  0.52                |  4024  |
|   0.0  |  0.48                |  3742  |

5. Now with the mapped authors dataframe. Each row has an author, and another author
mapped to her, or an author from her page. The pair is unique for each row. For 10996
unique authors, 203161 authors were found mapped to them; almost 18.5 mappings per
author.

6. *Missing data(!) - or missing gender information*
Out of 203161 rows, original author gender is known from 188635 rows (including multiple
  counting) and 176244 for mapped authors (including multiple counting). A little less
labels for mapped authors is expected; we don't know all the names.
