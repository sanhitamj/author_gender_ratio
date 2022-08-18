## Gender Ratio exploration.

A British journalist Mary Ann Sieghart writes in her book The Authority Gap that
women read books written by women more, and by men a little less. This gap is a
lot more pronounced when it comes to what books men read. That means, inherently,
women get less readers than men do. So women's voices are heard less than men's
voices. Women win less prestigious awards as well. Nothing unexpected here,
just another way to look at men's world!

This project is to scrape data from Amazon to see how many different authors does
this code find, what is their gender distribution, and do women get equally
recommended along with men? Say it starts with Chimamanda Ngozi Adichie (I
  recently read her Half of a Yellow Sun and liked the novel), and keeps a track
of - Customers Also Bought Items By (the recommended authors).

The reason I came up with this idea to check gender distribution, because along
with Chimamanda, many other women authors are suggested. Chimamanda is a feminist.
I also recently read Future Superhuman by Elise Bohan. Not many women authors are
suggested alongside her. The obvious difference is that Chimamanda writes fiction,
Elise writes non-fiction. (I was appalled at Elise Bohan's tone deafness, given
she works at Oxford, and also is a few years younger than me. I won't accuse her
of being a feminist either.)

Two anecdotes don't make a sample. So why not use some free time to scrape Amazon!

### Scraping -
1. Start with one author - Chimamand Ngozi Adichie. Find all the recommended authors
on her page.
2. Link those authors to her.
3. Visit the pages of all those authors. Find all the recommended authors on their pages.
4. Link those authors respectively to their respective reference author.
5. Rinse and repeat till we get, say 3141 authors.

Then start with Elise Bohan, and repeat. Assuming we'd find a completely independent
set of authors. Even if some are common, that's not the end of the world.

Currently these data will reside in a DataFrame, and a csv file.

### Analysis -

1. See how many women are recommended along side other women, and men.
2. Compare that with the gender ratio of the sample.
3. Whatever comes next...


### Code -
* environment.yml - I am conda fan!
* amazon_scraper.ipynb - testimonial of how bad I am at scraping; I'll clean it up
as I go along.
