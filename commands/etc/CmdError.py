import discord

from discord.ext import commands


class Music:
    class Empty_Queue(commands.CommandError):
        pass

    class NoPreviousTracks(commands.CommandError):
        pass

    class NoMoreTracks(commands.CommandError):
        pass

    class AlreadyConnectedToChannel(commands.CommandError):
        pass

    class PlayerIsAlreadyPaused(commands.CommandError):
        pass

    class PlayerIsAlreadyResumed(commands.CommandError):
        pass

    class TrackNotfound(commands.CommandError):
        pass

    class NoVoiceChannel(commands.CommandError):
        pass

    class Not_Requster(commands.CommandError):
        pass

    class Waiting_timeoute(commands.CommandError):
        pass

    class Not_playing(commands.CommandError):
        pass

    class Not_Seek_Live(commands.CommandError):
        pass


class Moder:
    class FaileUnwarn(commands.CommandError):
        pass

    class UseTempBan(commands.CommandError):
        pass


class Client:
    class Not_Notification(commands.CommandError):
        pass

    class Not_Commands(commands.CommandError):
        pass

    class Commands_NotHelping(commands.CommandError):
        pass

    class emoji_timeout(commands.CommandError):
        pass

    class message_timeout(commands.CommandError):
        pass

    class Not_Page(commands.CommandError):
        pass

    class Int_limited_Error(commands.CommandError):
        pass

class Season:
    class UserInData(commands.CommandError):
        pass
    
    class UserNotInData(commands.CommandError):
        pass

class Admin:
    class NotLoggingData(commands.CommandError):
        pass

