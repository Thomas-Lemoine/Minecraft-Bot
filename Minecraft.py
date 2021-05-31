#Started ~ 21st of Feb 2021

#Minecraft

import math
import numpy as np
import discord
import random
from discord.ext import commands,tasks
import os

intents = discord.Intents().all()

client = commands.Bot(command_prefix = ".", intents = intents)

client.coords = {}

@client.event
async def on_ready():
    await client.change_presence(activity= discord.Game("Triangulating strongholds..."))
    print("bot is ready!")

async def coordsinput(ctx):
    def isnum(v):
        return (type(v) is float) or (type(v) is int)
    
    def check(msg):
        coordinates = tupleofnums(msg.content)
  
        #print(f"authors are {msg.author} and {ctx.author}. channels are {msg.channel} and {ctx.channel}. msg.content[0] is {msg.content[0]}. msg.content[-1] is {msg.content[-1]}. Numbers is {Numbers}")
        return (msg.author == ctx.author 
        and msg.channel == ctx.channel
        and len(coordinates) == 3)
    
    msg = await client.wait_for("message", check=check)
    coordsint = tupleofnums(msg.content)
    return coordsint

@client.command(aliases = ["triangulate", "tri"])
async def Triangulation(ctx):

    await ctx.send("Enter the coordinates (x,z) as well as the angle of the throw f in the format (x, z, f): ")
    
    coords1 = await coordsinput(ctx)
    (x1,z1,f1) = coords1
    
    angle1 = f1 + 90
    secondthrowdist = ((250**2)+(500**2))**(1/2)
    secondthrowangle = 180*math.atan(1/2)/math.pi
    rec1 = (int(x1 + secondthrowdist*math.cos((math.pi/180)*(angle1 + secondthrowangle))), int(z1 + secondthrowdist*math.sin((math.pi/180)*(angle1 + secondthrowangle))))
    rec2 = (int(x1 + secondthrowdist*math.cos((math.pi/180)*(angle1 - secondthrowangle))), int(z1 + secondthrowdist*math.sin((math.pi/180)*(angle1 - secondthrowangle))))
    if (max(distance([0,64,0],[rec1[0],64,rec1[1]]),distance([0,64,0],[rec2[0],64,rec2[1]]))) == distance([0,64,0],[rec2[0],64,rec2[1]]):
        recommended_coords = rec2
    else:
        recommended_coords = rec1
    await ctx.send(f"The recommended second throw is at {str(recommended_coords)}")
    
    await ctx.send("Enter x,z and f for the second throw in the format (x, z, f): ")
    coords2 = await coordsinput(ctx)
    (x2,z2,f2) = coords2
    
    prediction_stronghold = triangulate(coords1, coords2)
    if prediction_stronghold == ("Error : Both angles are the same"):
        await ctx.send(prediction_stronghold)
    elif prediction_stronghold == ("Error : Incoherent coords"):
        await ctx.send(prediction_stronghold)
    else:
        await ctx.send(f"The stronghold is around {prediction_stronghold}.")
    
def triangulate(coords1,coords2):
    f1 = coords1[2]
    f2 = coords2[2]
    if (f1 == f2):
        return ("Error : Both angles are the same")
    angle1 = f1 + 90
    angle2 = f2 + 90
    xz1 = np.array([coords1[0],coords1[1]])
    xz2 = np.array([coords2[0],coords2[1]])
    uni_vect_1 = np.array(univect(convRad(angle1)))
    uni_vect_2 = np.array(univect(convRad(angle2)))
    rXs = np.cross(uni_vect_1,uni_vect_2)
    t = (np.cross(xz2 - xz1,uni_vect_2))/rXs
    v = (np.cross((xz2 - xz1),uni_vect_1))/rXs
    if (t >= 0) and (v >= 0):
        x = xz1 + t * uni_vect_1
        return makeint(x)
    else:
        return ("Error : Incoherent coords")

def convRad(deg):
    return math.pi*deg/180

def convDeg(rad):
    return 180*rad/math.pi

def univect(theta):
    return [math.cos(theta),math.sin(theta)]

def makeint(vector):
    ans = []
    for i in range(len(vector)):
        ans.append(int(round(vector[i])))
    return tuple(ans)

def distance(coords1,coords2):
    ans_0 = 0
    for i in range(len(coords1)):
        ans_0 += (coords2[i] - coords1[i])**2  
    return round((ans_0)**(1/2))

def nether_to_overworld(coords):
    return [int(coords[0]*8),int(coords[1]*8),int(coords[2]*8)]

def overworld_to_nether(coords):
    return [int(coords[0]/8),int(coords[1]/8),int(coords[2]/8)]

def angle_between_coords(coords1,coords2):
    return 180*math.atan2(coords2[1] - coords1[1],coords2[0] - coords1[0])/math.pi

def angbetvectors(f1,f2):
    angle1 = f1 + 90
    angle2 = f2 + 90
    vect1uni = [math.cos(convRad(angle1)),math.sin(convRad(angle1))]
    vect2uni = [math.cos(convRad(angle2)),math.sin(convRad(angle2))]
    angle = convDeg(math.acos(np.dot(vect1uni,vect2uni)))
    return angle

def tupleofnums(string):
    string += " "
    lst = []
    i = 0
    while i < len(string):
        if ((string[i].isdigit()) or (string[i] == "-")):
            number = string[i]
            tot = 0
            s = string[i]
            for j in range(1, len(string) - i):
                
                if string[i + j].isdigit():
                    tot += 1
                    s += string[i + j]
                else:
                    tot = 0
                    lst.append(int(s))
                    i += j
                    break
        i += 1
    return tuple(lst)


@client.command()
async def addcoords(ctx):
    def checkstring(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel and (type(msg.content) is str)
    await ctx.send("Enter the name of the new coords: ")
    name = await client.wait_for("message", check=checkstring)
    await ctx.send("Enter the coords in the format (x, y, z): ")
    xyz = await coordsinput(ctx)
    client.coords[name.content] = xyz
    await ctx.send(f'You have added the point {name.content} at the coordinates {xyz}.')

@client.command(aliases = ["coords"])
async def printcoords(ctx):
    coordslisting = "Here is the list of saved coordinates : "
    if client.coords == {}:
        await ctx.send('You have not saved any coordinates yet.')
        return client.coords
    for key in client.coords:
        coordslisting += f'{key} : {client.coords[key]}. '
    await ctx.send(coordslisting)

@client.command(aliases = ["save", "savecoords"])
async def _save(ctx, name, *, coordinates):
    coords1 = tupleofnums(coordinates)
    client.coords[name] = coords1
    await ctx.send(f'You have added the point {name} at the coordinates {coords1}.')

@client.command(aliases = ["dist", "distance"])
async def distancebetween(ctx, name1, name2):
    coords1 = client.coords[name1]
    coords2 = client.coords[name2]
    await ctx.send(f'The distance between points {name1} and {name2} is {distance(coords1,coords2)} blocks.')

@client.command(aliases = ["Delete", "remove"])
async def _remove(ctx, name):
    client.coords.pop(name, None)
    await ctx.send(f'You have removed the point {name}.')






#ADD SQL DATABASE TO STORE SAVED COORDINATES











#Add token
client.run("token")