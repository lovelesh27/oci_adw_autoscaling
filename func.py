import oci
import requests
import json
import time
import os
from base64 import b64decode
import io
import logging
from fdk import response

def handler(ctx, data: io.BytesIO = None):
    try:
        body = json.loads(data.getvalue())
        name = body.get("name")
    except (Exception, ValueError) as ex:
        logging.getLogger().info('error parsing json payload: ' + str(ex))

    logging.getLogger().info("Function handler triggered.....")
    logging.getLogger().info("Scale ADW triggered...")
    scale_adw()

    return response.Response(
        ctx, response_data=json.dumps(
            {"Result": "Function executed successfully."}),
        headers={"Content-Type": "application/json"}
    )

def scale_adw():
    logging.getLogger().info("Reached scale_adw function...")
    signer = oci.auth.signers.get_resource_principals_signer()
    database_client = oci.database.DatabaseClient(config={}, signer=signer)
    adw_ocid = "ocid1.autonomousdatabase.oc1.ash.enter_your_adw_ocid_here"
    get_autonomous_database_response = database_client.get_autonomous_database(
        autonomous_database_id=adw_ocid)

    current_cpu_core_count = get_autonomous_database_response.data.cpu_core_count
    new_cpu_core_count = current_cpu_core_count + 1

    logging.getLogger().info("Current CPU_CORE_COUNT: " + str(get_autonomous_database_response.data.cpu_core_count))

    logging.getLogger().info("Updating CPU_CORE_COUNT to: " + str(new_cpu_core_count))

    update_autonomous_database_response = database_client.update_autonomous_database(
        autonomous_database_id=adw_ocid,
        update_autonomous_database_details=oci.database.models.UpdateAutonomousDatabaseDetails(
            cpu_core_count=new_cpu_core_count))

    success = 0

    for loop in range(5):
        if(current_cpu_core_count == new_cpu_core_count):
            success = 1
            break
        else:
            logging.getLogger().info("" + str(loop+1) + ". Checking if operation completed...")
            time.sleep(5)
            get_autonomous_database_response = database_client.get_autonomous_database(
                autonomous_database_id=adw_ocid)
            current_cpu_core_count = get_autonomous_database_response.data.cpu_core_count

    if(success == 1):
        logging.getLogger().info("Successfully updated CPU_CORE_COUNT to: " + str(get_autonomous_database_response.data.cpu_core_count))
    else:
        logging.getLogger().info("Could not update the CPU_CORE_COUNT in time, please check this from OCI Console.")
