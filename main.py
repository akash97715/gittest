I just modified the prompt for better similarity search result, now I am getting the document as 1st citation. I suggest if you see such type of issue from next time, prompt engineering is the solution. 

Technically we need to understand here that at the end of the day to get the revelent chunks you have to pass the good prompts and least we have to experiment with some prompts because by changing prompt only you will be able to change the behaviour of similarity search score, let me know if you need more clarity around this? Also I have seen u r giving around 2.5k md5 during search which add more complexity while sementic search.

BEST PRACTICES: DON’T USE ?(special characters) etc in the prompt if you have small prompts because these special characters bring lot of noise during the sementic search. 
