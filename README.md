The second trading algo I've devoloped using Selenium and Alpaca again. This one focuses on the show "Mad Money" and its host Jim Cramer. 
This little python script is able to scrape the stock picks of Cramer from the official Mad Money stock screener. It's currently grabbing Quarterly picks. We then seperate the stocks in to two categories depending on their ratings, Buy and Sell. 

In simple, we just do the opposisite of the what Cramer suggests. Placing an order via the Alpaca API to our paper trading account. This is a popular strategy, but I believe that this is a somewhat unique way of implementation to accomplish the same goal as others.
I hope to add more order logic, options, and account features while also improving on the strategy itself.
