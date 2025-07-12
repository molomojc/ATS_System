Information about how cv_matcher vectorising works 

What is TF-IDF? NLP model used for convert text into numeric vectors 
1 Dimension each vector resuling of how each word is important is across the entire word
meaning if two documents have words which have/are similar they will have high score

TF-IDF - Inverse Document Frequency 

TF refers to: How often a word apears accross the documents
(Term Frequency)
Measured by the scary math formular
TF(t,d) = (Number of times it appears a word appears in one document) /(Total Number of words)

e.g 
i love coding because coding is Fun
hence TF = (2)/ 7 , Simple right : )

IDF -> INVERSE Document Frequency
(How important is each word across all the document ?)
the scry formular
IDF(t) = log(N/1 + df(t)) WHERE,
N = total number of documents our case 2
df(t) -> number of documents which contain this word(t)

hence TF-IDF = 
high number if words match
low number if words rarely match

example 
of the two documents

DOC1: i love machine learning
DOC2: Machine learning is great
DOC3: I love deep learning too

Calculate TF:
DOC1
1. love: 1/4
2. machine 1/4
3. learning 1/4
4. i : 0 -> not important 
DOC2
1. Machine: 1/4
2. learning: 1/4
3. is: 1/4
4. great: 1/4
DOC3
1. love: 1/4
2. deep: 1/4
3. learning: 1/4
too: 1/4

hence calculate the IDF 
df(t) how many times does it occure in all documents ?
Term                  df(t)        IDF(t)
deep                   1             log(3/1 + 1) + 1 
great                  1             same
is                     1              same
learning               3            log(3/4) + 1
etc...

now calculating TF-IDF
DOC1:
love: 1/4 * 1 = 0.25
etc..

which result in the vector
arrange all words in alphabetic order
[ ['deep' 'great' 'is' 'learning' 'love' 'machine' 'too']]
now the resulting thingy for each
[     0    0        0     0.25       0.25      0.25   0]

#normalize the vectors 
you get
[0    0     0   0.58     0.58     0.58    0]
then doing each of the documents like this

you get a matrix 
row = documents 
col: words in alphabetic order 

now calculate the cosine score (LINEAR ALGEBRA)
cosine_similarity(A,B) = A . B / (|A| * |B|)
where A -> represent each vector (sentence/ document)

e.g doc1 = [0, 0, 0, 0.58, 0.58, 0.58, 0]   # "I love machine learning"
doc2 = [0, 0.71, 0.71, 0.35, 0, 0.35, 0] # "Machine learning is great"

find the dot product
= (0×0) + (0×0.71) + (0×0.71) + (0.58×0.35) + (0.58×0) + (0.58×0.35) + (0×0)
= 0 + 0 + 0 + 0.203 + 0 + 0.203 + 0
= **0.406**

now find the maginitude of each vector 
||A|| = 1.004
||B|| 1

hence find the cosine cosine_similarity
Step 3: Final Cosine Similarity
you get 
= 0.361

a number between 0 - 1
where 1 = 100%
and 0 = 0% words are similar