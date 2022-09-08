import interactions


async def create_managed_emote(emoji, guild: interactions.Guild, channel: interactions.Channel, existing_msg=None) \
        -> interactions.Emoji:
    if ":" in emoji:
        emo_id = emoji.split(':')[-1][:-1]
        try:
            emo = await guild.get_emoji(int(emo_id))
        except Exception as e:
            raise ValueError(f"got nonsense emoji value '{emoji}'")
    else:
        # assuming this is default
        emo = interactions.Emoji(name=emoji)
        if existing_msg is None:
            msg = await channel.send("testing emoji")
        else:
            msg = existing_msg
        try:
            if existing_msg is not None:
                await existing_msg.create_reaction(emo)
            else:
                await msg.create_reaction(emo)
        except Exception:
            raise ValueError(f"got nonsense emoji value '{emoji}'")
        if existing_msg is not None:
            pass
        else:
            await msg.delete(reason="testing emoji message being destroyed")
    return emo
