AI Summary Info
=============================================

#### Overview Info:
- 53% of dockets have an abstract summary that exists
- some dockets have one or more htm files that may or may not have a docket summary
- the problem with this is that some dockets have no htm files, some have one, and others have many htm files with more than one summary
- it appears to be much easier to generate a summary for dockets without an existing abstract summary in the .json file

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
