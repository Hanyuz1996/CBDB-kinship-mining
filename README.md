# CBDB-kinship-mining
Kinship Data Analysis for CBDB Data

1.	Data Overview
1)	Biog Main:
This table contains basic biographical information: name, id, gender, tribe, birth year, death year, posting etc, in total 56 attributes. Every person in the table can be located by index year on the timeline. Totally, table includes 366588 people, with index years ranging from -645 to 1969. There is an obvious unbalanced distribution between gender: Only 48641 of all people are female, and most of them only has surname.
 
2)	Kinship Codes:
Up to now, there are 479 types of kinship in this table. Most of them are derived from 9 basic kinship: e(self), Father, Mother, Son, Daughter, Z(Sisters), Brothers, Husband, Wife(Concubine). With basic kinship (Uppercase) and auxiliary symbols (Lowercase, numbers, special numeric), we can illustrate kinship that is more complex. Upstep, dwnstep, marstep, colstep are used to show the seniority and marriage.
3)	Kin Data:
Kin Data records the kinship between people in Biog Main. The structure is:
Core(personid, kinid, kincode) + sources + editorial information
People with personid and kinid has the relationship as kincode. There are 482388 kinship have been recorded, and 239568 pairs appear (>99%). Totally 409 types of kinship appear. Kinships concentrates on several specific types (more than 10000 times) while 46 types of kinship only appear once. Most common kinships are:

2.	Kinship Mapping
1)	Basic Principles
Since there are only 10% people in database are female and traditional patriarchy holds sway, we’d like to draw the map in the way of Chinese traditional family tree. That is, each person have a rank in his family based on his/her seniority. The whole map is from left to right (or up to down) and one tier matches one seniority. (When without ambiguity, it can match 2 or more seniority, like there are only one people in both the first and the second seniority.) Men should only been seen in only one map, and women can be seen in different maps (example: Husband’s family and Original family).
2)	Family Classifying
Based on the common idea that people who have relationships between each other should be in the same family, to make sure we do not take female’s information of original family into her husband’s family or conversely, we have some strict rules when classifying. Since most relationship between people are basic relationships, after dealing with the strict rules, we only lose little information. Before all, we throw away all vague kinships that cannot provide definite seniority.
For male:
a)	For every kinship information, if kinid corresponds to a man, then they are in not one family, if the kinshipcode do not include anyone in ‘WMCHAPZ’(which means these two men are linked with a marriage kinship), or kinid corresponds to his daughter’s descendant(who should be in the daughter’s husband’s family).
b)	For every kinship information, if kinid corresponds to a woman, we only consider the situation that the basic kinship of it is one of “MWCDZ”. For these basic kinship, we can easily judge whether this is the woman’s husband’s family or original family. For other kinship, we just throw them away.
For female, first we define “ForbidList”. When the woman is in her original family, ForbidList includes {"H","S","D","P","A","G-","W"}; when she is in her husband’s family, it includes {"B","Z","G+","F","M","K","P"}; otherwise it can be seen as a empty set. We do not consider kinships with code in ForbidList. And then:
a)	If kinid corresponds to a man, we use the same rule when man meets man
b)	If kinid corresponds to a woman, we only consider the situation that the basic kinship of it is one of “MDZ”. For these basic kinship, we can easily judge whether this is the woman’s husband’s family or original family. For other kinship, we just throw them away.
From any man, we can start breadth-first search and find his family information, including family members’ id and relationship between them.
With the data in CBDB now, we can cut all people (appear in both BIOG_MAIN and Kin Data) into 34,440 families.
3)	Family Combine
Family Combine should be used in these two situation:
a)	In family classifying, because of our strict rules, some men may appear in different families. As our basic principles tell, these different families, in fact, should be just one family. So we need to combine these families into one.
b)	When we get new kin data, we just need first to do family classifying with these data. Then we do family combine with new results and old results. Finally we can get combined families. This should be much more faster than do family classifying again with whole data.
We use one simple principle to do family combine. That is, one man should only appear in one family. After family combine, We have about 33,000 families, and the biggest one contains more than 9000 people.
4)	Seniority determination
With the information in kindatacode (Upstep, dwnstep, marstep, colstep), we can determine the relative seniority of the kinship. Choose arbitrary man in the family to be of 0 seniority, we do breadth-first search and determine the seniority of everyone in the family. For women, we define two seniority: one in husband’s family and one in original family. Since there are women whose husband’s family is also her original family, these two seniority should be count separately to exclude conflict. In this way, we will not find conflicts when determining seniority if the data is all correct.
5)	Map drawing
We use graphviz to draw the map. Before that, we use the seniority information to create the code for graphviz. We demand people of same seniority in the same tier, male denoted by rectangular, female denoted by red rectangular and show relationship from high seniority to low seniority majorly. For most family, we can draw beautiful maps. When there are too many redundant relationships, map may not be drawn under the requirement that people of same seniority in the same tier. We attach the map of Tiemuzhen’s family as an example.
3.	Redundant kinship removing
Actually, there are many redundant kinship for a kinship map in the original data. For example, we may have three kinship: A is B’s father, B is C’s father, and A is C’s grandfather. Obviously, the third kinship is redundant: we can derive it from the other two kinship, and it gives no more useful information. We have find about 14,000 redundant kinship in the data. We strong recommend that user first remove as much as possible redundant kinship and then do kinship mapping, since we have not developed the function to remove kinship from existed map.
 
