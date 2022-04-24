from asyncio.windows_events import NULL
import random
from urllib import response
from django.shortcuts import render
from django.contrib import messages

from .models import AnnouncedPuResults, PollingUnit, Ward, Lga, States

import functools
import uuid
from datetime import datetime
import json
from urllib.request import urlopen

def individual_polling_result(request):
    results = []
    polling_results = AnnouncedPuResults.objects.all()
    for result in polling_results:
        context = {}    
        polling_data = PollingUnit.objects.filter(uniqueid = result.polling_unit_uniqueid)[0]    
        ward_data = Ward.objects.filter(ward_id = polling_data.ward_id)[0]
        lga_data = Lga.objects.filter(lga_id = polling_data.lga_id)[0]
        state_data = States.objects.filter(state_id = lga_data.state_id)[0]

        context['id'] = result.result_id
        context['party'] = result.party_abbreviation
        context['score'] = result.party_score
        context['unit'] = polling_data.polling_unit_name
        context['ward'] = ward_data.ward_name
        context['lga'] = lga_data.lga_name
        context['state'] = state_data.state_name
        results.append(context)

    return render(request, 'polling_result/individual_polling_result.html', {'results': results})

def summed_total_result(request, lga_id=0):
    lgas = Lga.objects.all()
    if lga_id == 0:
        return render(request, 'polling_result/total_result.html', {'lgas': lgas})
    
    lga = Lga.objects.filter(lga_id = lga_id)[0]
    context = {}
    state = States.objects.filter(state_id = lga.state_id)[0]    
    polling_units = PollingUnit.objects.filter(lga_id = lga_id)
    units_results = []
    for unit in polling_units:
        try:
            result = AnnouncedPuResults.objects.filter(polling_unit_uniqueid = unit.uniqueid)
            # print(result)
        except:
            result = []
        if len(result) != 0:
            for val in result:
                units_results.append(val.party_score)

    if len(units_results) != 0:
        summed_lga_score = functools.reduce(lambda x, y: x + y, units_results)
        context['lga'] = lga.lga_name
        context['state'] = state.state_name
        context['score'] = summed_lga_score
    else:
        context['lga'] = lga.lga_name
        context['state'] = state.state_name
        context['score'] = 0
    return render(request, 'polling_result/total_result.html', {'result': context, 'lgas': lgas})

def new_result(request):    
    if request.method == 'POST':
        url = 'https://geolocation-db.com/json'
        try:
            response = urlopen(url)
            data = json.load(response)

            ip = data['IPv4']   
            lat = data['latitude']
            long = data['longitude']
        except:
            ip = NULL
            lat = NULL
            long = NULL
        res_unit = request.POST['polling_unit']
        res_ward = request.POST['ward']
        res_lga = request.POST['lga']
        res_state = request.POST['state']
        agent = request.POST['agent']
        date_entered = datetime.now().isoformat()
        
        existing = {'state': '', 'lga': '', 'ward': ''}
        states = States.objects.filter(state_name = res_state)
        if len(states) > 0:
            state = states[0]
            existing['state'] = state
            lgas = Lga.objects.filter(state_id = state.state_id, lga_name = res_lga)
            if len(lgas) > 0:
                lga = lgas[0]
                existing['lga'] = lga
                wards = Ward.objects.filter(lga_id = lga.lga_id, ward_name = res_ward)
                if len(wards) > 0:
                    ward = wards[0]
                    existing['ward'] = ward
                    polling_unit = PollingUnit.objects.filter(polling_unit_name = res_unit, ward_id = ward.ward_id)
                    if len(polling_unit) > 0:
                        messages.add_message(request, messages.ERROR, "Polling unit already exits")
                        print('got here')
                        return render(request, 'polling_result/new_result.html', None)
        
        items = request.POST        
        for key, val in items.items():
            if val == '':
                messages.add_message(request, messages.ERROR, "All fields must be filled")
                return render(request, 'polling_result/new_result.html', None)
        score_dict = {'PDP': request.POST['pdp'], 'DPP': request.POST['dpp'],
                      'PPA': request.POST['ppa'], 'CDC': request.POST['cdc'],
                      'JP': request.POST['jp'] }

        if existing['state'] == '':
            # ensures state_id is unique if its a new state
            ids = []
            for state in States.objects.all():
                ids.append(state.state_id)    
            state_id = random.randint(1, 255)
            while state_id in ids:
                state_id = random.randint(1, 500)
            new_state = States(state_id = state_id, state_name = res_state)
            new_state.save()
            existing['state'] = new_state

        if existing['lga'] == '':
            # ensures lga_id is unique if its a new lga
            ids = []
            for lga in Lga.objects.all():
                ids.append(lga.lga_id)    
            lga_id = random.randint(1, 255)
            while lga_id in ids:
                lga_id = random.randint(1, 500)
            new_lga = Lga(lga_id = lga_id, lga_name = res_lga,
                         state_id = existing['state'].state_id, entered_by_user = agent, 
                         date_entered = date_entered, user_ip_address = ip)
            new_lga.save()
            existing['lga'] = new_lga

        if existing['ward'] == '':
            # ensures ward_id is unique if its a new ward
            ids = []
            for ward in Ward.objects.all():
                ids.append(ward.ward_id) 
            ward_id = random.randint(1, 255)
            while ward_id in ids:
                ward_id = random.randint(1, 500)
            new_ward = Ward(ward_id = ward_id, ward_name = res_ward, lga_id = existing['lga'].lga_id,
                        entered_by_user = agent , date_entered = date_entered, user_ip_address = ip)
            new_ward.save()
            existing['ward'] = new_ward

        # ensures ward_id is unique if its a new ward
        ids = []

        for unit in PollingUnit.objects.all():
            ids.append(unit.polling_unit_id) 
        unit_id = random.randint(1, 255)
        while unit_id in ids:
            unit_id = random.randint(1, 500)

        polling_data = []
        for key, value in score_dict.items():
            context = {}    
            unit = PollingUnit(polling_unit_id = unit_id, ward_id = existing['ward'].ward_id,
                               lga_id = existing['lga'].lga_id, polling_unit_name = res_unit, 
                               lat = lat, long = long, entered_by_user = agent,
                               date_entered = date_entered, user_ip_address = ip)
            unit.save()
            print(key)
            result = AnnouncedPuResults(polling_unit_uniqueid = unit.uniqueid, party_abbreviation = key, party_score = value,
                                    entered_by_user = agent, date_entered = date_entered, user_ip_address=ip)
            result.save()
            context['id'] = result.polling_unit_uniqueid
            context['party'] = result.party_abbreviation
            context['score'] = result.party_score
            context['unit'] = unit.polling_unit_name
            context['ward'] = existing['ward'].ward_name
            context['lga'] = existing['lga'].lga_name
            context['state'] = existing['state'].state_name          
            polling_data.append(context)

        messages.add_message(request, messages.SUCCESS, "Polling unit result added successfully\
                            with the following details")
        return render(request, 'polling_result/new_result_success.html', {'results': polling_data})

    return render(request, 'polling_result/new_result.html', None)