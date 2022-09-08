import interactions
from interactions import extension_command

from Config import get_server_id

# set to null when goes global
guild_id = get_server_id()


class ProfCommand(interactions.Extension):
    def __init__(self, client):
        self.bot = client

    @extension_command(name="hemann", description="""
    not great with names
    """, scope=guild_id)
    async def _hemann(self, ctx):
        await ctx.send(
            "I'm not naturally great with names. "
            "But I try really hard at it and I'm pretty relentless at asking for them when I don't know it. "
            "I suppose it's possible you were there and vocal and active and it's just blanked out of my memory."
            "That's unfalsifiable. But I think 13 out of 15 in terms of class participation when "
            "I wouldn't recognize you on the back of a milk carton is fairly generous.\n \n --JBH")

    @extension_command(name="lerner", description="""
    best piazza response
    """, scope=guild_id)
    async def _lerner(self, ctx):
        await ctx.send(
            "Giving 🙄  you 🙇😱 further 😠 examples would 💢  defeat the 👏😟 purpose of 👉 the question, "
            "which is for you ☝️  read and 👏👏 figure out 😲 what it means, and what it’s 💯✋ asking ❔"
            "😭 for, 😡 so 💁that you can 📑 solve the ⚕🕑 problem. Asking ❔ someone else 🤷😯 to work 🏢 "
            "through 👉🤢 the ❌  examples for you is like 🙄  asking 💬 them 🖋️ to go 🏃 to 😀 the 🏋️‍♂️  "
            "gym 💪 for 👏 you: 😣 they’ll 😄🙎 get 🙄 the benefit 😩 of the 👏 exercise, 🤸 and 😡 you ☝won’t. "
            "<:lerner:761014749142974505>")

    @extension_command(name="lerner2", description="""
    let me gently sugggest
    """, scope=guild_id)
    async def _lerner2(self, ctx):
        await ctx.send(
            'Let me gently suggest that this is a bad question to ask, especially in advance of the exam.'
            'The typical meaning students want for “curving an exam” is simply'
            '“give us more points even if we got things wrong”, aka grade inflation. The actual meaning of'
            '“curving an exam” is to force the exam grades to conform to a specific grade distribution'
            '(a pre-specified average and standard deviation, such that the histogram of grades forms a'
            'particular pre-chosen curvy shape), aka grade deflation. Neither of those is a pedagogically good outcome.'

            'We’ve written enough exams over the years that we can calibrate the exam to be'
            '“roughly the same difficulty” as preceding years’ exams, and we know roughly how those grades turned out.'
            'And if the grades this year turn out roughly the same,'
            'then we won’t be artificially changing the grades for you at all. Ideally,'
            'an “80% on the exam” (just to pick a number) means you’ve mastered 80% of what we’ve taught so far.'
            'Changing the grades by artificially inflating or deflating them decouples their value from any meaningful'
            'feedback you could get from them, other than a good feeling for “getting a high number”.'

            'Amal and I are perfectly happy for all of you to earn 100%s on the exam'
            '(we’d be delighted if everyone mastered everything we’ve taught!),'
            'and are perfectly willing to give out 0%s if those grades were earned'
            '(we’d be very disappointed, and it’s exceedingly unlikely, but it could happen).'
            'The only reason she or I ever modify the grades of an exam is if we recognize'
            'that a question was typoed, broken, or somehow much harder than intended and'
            'practically everyone gets it wrong for some reason or another, and we have to'
            'rectify a mistake that we made.'
            'And there’s absolutely no way for us to know that in advance of grading the exam!')

    @extension_command(name="shiver", description="""
    shiver makes u shiver
    """, scope=guild_id)
    async def _shiver(self, ctx):
        await ctx.send('Who should I thank? My so-called "colleagues," '
                       'who laugh at me behind my back, all the while becoming famous on my work? '
                       'My worthless graduate students, whose computer skills appear to be limited '
                       'to downloading bitmaps off of netnews? My parents, who are still waiting for '
                       'me to quit fooling around with computers, go to med school, and become a radiologist? '
                       'My department chairman, a manager who gives one new insight into and sympathy '
                       'for disgruntled postal workers? My God, no one could blame me -- no one! -- '
                       'if I went off the edge and just lost it completely one day. I couldn\'t get '
                       'through the day as it is without the Prozac and Jack Daniels I keep on the shelf, '
                       'behind my Tops-20 JSYS manuals. I start getting the shakes real bad around 10am, '
                       'right before my advisor meetings. A 10 oz. Jack \'n Zac helps me get through the '
                       'meetings without one of my students winding up with his severed head in a bowling-ball bag. '
                       'They look at me funny; they think I twitch a lot. I\'m not twitching. '
                       'I\'m controlling my impulse to snag my 9mm Sig-Sauer out from my day-pack '
                       'and make a few strong points about the quality of undergraduate education in Amerika. '
                       'If I thought anyone cared, if I thought anyone would even be reading this, '
                       'I\'d probably make an effort to keep up appearances until the last possible moment. '
                       'But no one does, and no one will. So I can pretty much say exactly what I think. '
                       'Oh, yes, the acknowledgments. I think not. I did it. I did it all, by myself.')

    @extension_command(
        name="shesh",
        description="""
    hw over thanksgiving?
    """, scope=guild_id)
    async def _shiver(self, ctx):
        await ctx.send("I struggle to think of even one situation "
                       "where a company would move a release deadline because of the personal, "
                       "optional travel plans of its engineers. "
                       "This serves as a reminder to me that perhaps trying to be understanding "
                       "and pushing deadlines benefits nobody. "
                       "It seems that being accommodating creates the expectation "
                       "of even more accommodation. Lesson learned.")


def setup(client):
    ProfCommand(client)
