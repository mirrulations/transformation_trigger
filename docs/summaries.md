AI Summary Info
=============================================

### Overview Info:
- 53% of dockets have an abstract summary that exists(60% for 2023 to present)
- Some dockets may not have meaningful abstract summaries either(they can be a word or 2 simply saying 'closed')
- some dockets may have more than one htm file
- the problem with this is that if dockets have more than 1 htm file we will have to figure out how to generate a summary from those multiple htm files leading us towards a potential AI summary.
- it appears it might be easier to generate a summary for dockets without an existing "meaningful" abstract summary in the .json file or just generate an AI summary for all dockets.

### If we implement an AI summary feature:
- AWS Bedrock is useful for several purposes; however, it provides access to existing AI models to use and implement in things like our Lambda functions
- Amazon has their own models which include both text and visual models, however one named Amazon **Nova Lite** is a text-only model and would be cost-effective since all we need is a text-based model

### Cost info
- 259k total dockets
- 47% brings the number down to about 122k
- this number can be further reduced to only generate summaries from 2023 to the present
- Amazon Nova Lite is cost-effective and appears that it would cost no more than $37
    - According to Cost Explorer:
        - Nova Lite input tokens of 122k uses would cost $7.32
        - Nova Lite output tokens of 122k uses would cost $29.28
- This cost would of course decrease if we only do recent dockets (such as 2023 to present)
