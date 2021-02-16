# IPO-analysis-proj


1. What does the project set out to study?

With the wave of IPOs (Initial Public Offerings) in recent years, the project aims to perform an exploratory data anlysis on recent IPOs and see if there are any interesting insights about their timing, industry, company standing (established), and other factors. In addition to the overall market trend, the project also takes a look at a few big IPOs (Snowflake, Unity Software, etc.) that happened recently and explore the correlations existed among a variety of performance metrics.

2. What we Discovered?

For the exploratory data anlysis part, we found that in the past 2 years: 1) Wednedsay and Thusday has the most IPO filed; 2) Companies tend to file IPO on the second half of the year (Q3Q4), especially from September to November; 3) 60% of the companies that filed IPO was either in healthcare or financial services sector; 4) There are no a single/a few investment banks overwhelmingly employed as IPO managers.
For analyzing key attributes and performances metrics of IPO companies, we originally make assumption that most of the correlations between attributes should be positive (and moderate). This assumption was partially confirmed but we have a striking counterexample EBITDA, which is negatively correlated to a lot of other attributes in a strong way (with correlation coefficent close to -1).

3. How to expand or augment the project?

One way to expand the project is to collected more data on the 730 recently filed IPOs. Specifically, I want to collect CEO info like age/salary (I actually already wrote working scraper for this but it was dropped due to long scraping time), stock price history for the first 3day/week/month after the IPO, key performance stats (like those in the top_keystats.csv) and more. With stock data for a larger timeframe and data over specific (critical) period, we can potentially develop more profound understanding on those IPOs and search for relationships among the attributes.
Moreover, since we notice how COVID can possibly affect financial metrics like EBITDA, we can scale up the project by comparing stock performance at different stages of the pandemic and how does the general IPO trend shifts.
