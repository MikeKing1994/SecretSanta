from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, get_object_or_404
from .models import ParticipantName
from .models import ParticipantEmail
from emailTemplate import sendemail
from django.utils import timezone
import json
import random

def index(request):
    latest_name_list = ParticipantName.objects.all()
    latest_email_list= ParticipantEmail.objects.all()
    entrants = dict(zip(latest_name_list, latest_email_list))
    template = loader.get_template('creativeRutApp/index.html')
    context = {'entrants': entrants}
    return render(request, 'creativeRutApp/index.html', context)
    
def listAppend(request):   
    if request.method == 'POST':
        form = request.POST
        print(form)
        if form:
            inputName = form['inputName']
            inputEmail = form['inputEmail']
            #create the new name
            newName = ParticipantName.objects.create(ParticipantName=inputName, pub_date= timezone.now())
            #Getting the Id by the name causes an error if you try to add a duplicate name
            newNameInDB = ParticipantName.objects.get(ParticipantName=inputName).id
            #add the email in, this has a foreign key to the name
            newEmail= ParticipantEmail.objects.create(pName_id=newNameInDB, pEmail = inputEmail)
            newName.save()
            newEmail.save()
    return index(request)

    
def listDelete(request):   
    if request.method == 'POST':
        form = request.POST
        #get the name to delete from the form
        nameToDelete=form['delete']
        print(nameToDelete)
        #get the email that is the foreign key of this name
        objectNameToDeleteId = ParticipantName.objects.get(ParticipantName=nameToDelete).id
        emailToDelete=ParticipantEmail.objects.get(pName_id=objectNameToDeleteId).pEmail
        print(nameToDelete, emailToDelete)
        sendemail(['michaelj.king@btinternet.com'], [emailToDelete], [],
              subject='Secret Santa Deletion Notification', 
              message='Hi ' + nameToDelete+ ' this is a message to let you know that your name has been removed from the secret santa website. Please navigate to https://localhost:8000/creativeRutApp to add your name',
              login='michaelj.king1994@gmail.com',
              password= 'kvQn9gFq')
        print('attempted to send email, didn\'t throw an error')
        #get the name
        objectNameToDelete=ParticipantName.objects.get(ParticipantName=nameToDelete)
        #delete the name
        objectNameToDelete.delete()
        print('got further than the deletion')
    return index(request)
    #Finish off the deletion button backend here

#Here I'm keeping triggerDraw and Draw seperate so that later if i want I can set the draw to trigger at a certain time    
def triggerDraw(request):
    if request.method == 'POST':
        form = request.POST
        drawBool=form['trigger']
        if drawBool:
            return draw(request)
        else:
            return index(request)
            
#this function will run after a transaction has been processed and will determine if the new state of the graph leads to an invalid state
#if the state is valid, it returns true and the transaction will be committed, if not the transaction will be rolled back
def isStateValid(newGiverList, newReceiverList, newAvailableArcList):
    #possibleGivers/receivers are the arcs that can still give/receive according to available arc list
    #assume the validity is true, unless we set it to 0 later
    validity= True
    possibleGivers = []
    possibleReceivers = []
    for arc in newAvailableArcList:
        possibleGivers.append(arc[0])
        possibleReceivers.append(arc[1])
    for givingNode in newGiverList:
        if givingNode not in possibleGivers:
            validity= False
    for receivingNode in newReceiverList:
        if receivingNode not in possibleReceivers:
            validity= False        
    return validity

#this function takes the currently available arcs and tries to see if selecting that arc will leave you with an isolated node
def tryAnArc(arcToTry,giverList, receiverList, availableArcList):
    arcReceiver = arcToTry[1]
    arcGiver = arcToTry[0]
    
    #define a new instance of the lists, so that if we conclude the arc choice is invalid we can just return the original list
    newAvailableArcList = list(availableArcList)
    newGiverList=list(giverList)
    newReceiverList=list(receiverList)
    
    #as an arc XY has been selected, we need to remove all arcs ending in Y and all arcs ending in X
    for arc in availableArcList:
        if arc[1] == arcReceiver:
            newAvailableArcList.remove(arc)
        elif arc[0] == arcGiver:
            newAvailableArcList.remove(arc)
            
    #As X has given a present, they must be removed from the giver list and similar for Y receiving
    newReceiverList.remove(arcReceiver)
    newGiverList.remove(arcGiver)
    #now our 'transaction has been actioned, we need to check if this leaves any isolated nodes
    #an isolated node is a node that needs to give, but can't giv
    #or a node that needs to receive that can't receive
    if isStateValid(newGiverList, newReceiverList, newAvailableArcList):
        #commit the transaction
        return True, newGiverList, newReceiverList, newAvailableArcList
    else:
        #rollback the transaction
        return False, giverList, receiverList, availableArcList
            
#function to send an email to an individual person from the draw
def sendIndividualDrawEmail(pairing, request):
    sender = pairing[0]
    print('sender',sender)
    receiver = pairing[1]
    message='Hi ' + str(sender) + ' this is a message to let you know that you have drawn ' + str(receiver) + ' as your draw for the King family secret santa! Don\' let them know!'
    print(message)
    try:
        sendemail(['michaelj.king@btinternet.com'], [str(sender)], [],
              subject='Secret Santa Surprise Draw!', 
              message=message,
              login='michaelj.king1994@gmail.com',
              password= 'kvQn9gFq')
    except Exception as e:
        print(e)
    return     
                   
#function to send emails to all the people
def sendDrawEmails(finalArcList, request):
    #currently final arclist is the querydict of the names, need to turn that into email pairings here
    emailPairingList=[]
    for namePairing in finalArcList:
        #For each name pairing, take the sender and receiver name
        senderName = namePairing[0]
        receiverName = namePairing[1]
        print('senderName from senddrawemails',senderName)
        #go to the database and get the emails that correlate to those names
        senderNameInDB = ParticipantName.objects.get(ParticipantName=senderName).id
        print('senderNameinDB', senderNameInDB)
        senderEmail= ParticipantEmail.objects.get(pName_id=senderNameInDB)
        print('senderEmail',senderEmail)
        receiverNameInDB = ParticipantName.objects.get(ParticipantName=receiverName).id
        receiverEmail= ParticipantEmail.objects.get(pName_id=receiverNameInDB)
        #add the email pairing to the list
        emailPairingList.append((senderEmail,receiverEmail))   
    print('emailPairingList',emailPairingList)
    for pairing in emailPairingList:
        sendIndividualDrawEmail(pairing, request)
    context={'finalArcList':finalArcList}
    return render(request,'creativeRutApp/drawResult.html', context)

            
def draw(request):
    #need to initialise by getting all the list of names into originalNameList
    latest_name_list = ParticipantName.objects.all()
    print(latest_name_list)
    originalNameList = []
    for name in latest_name_list:
        originalNameList.append(name)
    print(originalNameList)
    
    finalArcList = []
    
    #List of people who can still give a present
    giverList = list(originalNameList)
    
    #list of people who can still receive a present
    receiverList = originalNameList
    
    #List of arcs that can still be chosen from, in the form AB, where A will buy a present for BaseException
    availableArcList = []
    for name in originalNameList:
        for name2 in originalNameList:
            availableArcList.append((name,name2))
    for name in originalNameList:
        availableArcList.remove((name,name))
    
    #try an arc, if the arc leads to an invalid state, remove the arc from availableArcList and try again
    #if this process causes availableArcList to run out of arcs, throw an error
    #if the arc succeeds, update the lists appropriately and append the chosen arc to the finalArcList
    try:
        while len(availableArcList)!= 0:
            arcToTry=random.choice(availableArcList)
            validity, newGiverList, newReceiverList, newAvailableArcList = tryAnArc(arcToTry,giverList, receiverList, availableArcList)
            if validity:
                #update the lists, append the chosen arc to finalArcList, 
                giverList = list(newGiverList)
                receiverList = list(newReceiverList)
                availableArcList = list(newAvailableArcList)
                finalArcList.append(arcToTry)
            else:
                #delete the arc from the arclist 
                availableArcList.remove(arcToTry)
    except Exception as e:
        print(e)
        return e
    return sendDrawEmails(finalArcList, request)