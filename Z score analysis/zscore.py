import email_conf, json, time, math, statistics
from boltiot import Email, Bolt

def compute_bounds(history_data,frame_size,factor):
    if len(history_data)<frame_size :
        return None

    if len(history_data)>frame_size :
        del history_data[0:len(history_data)-frame_size]
    Mn=statistics.mean(history_data)
    Variance=0
    for data in history_data :
        Variance += math.pow((data-Mn),2)
    Zn = factor * math.sqrt(Variance / frame_size)
    High_bound = history_data[frame_size-1]+Zn
    Low_bound = history_data[frame_size-1]-Zn
    return [High_bound,Low_bound]

mybolt = Bolt(email_conf.API_KEY, email_conf.DEVICE_ID)
mailer = Email(email_conf.MAILGUN_API_KEY, email_conf.SANDBOX_URL, email_conf.SENDER_EMAIL, email_conf.RECIPIENT_EMAIL)
history_data=[]

while True:
    try:
        response = mybolt.analogRead('A0')
        data = json.loads(response)
        print ("This is the value "+data['value'])
        sensor_value = int(data['value'])
        bound = compute_bounds(history_data,email_conf.FRAME_SIZE,email_conf.MUL_FACTOR)
        history_data.append(int(data['value'])) 
        
        
        if not bound:
            print("Not enough data to compute Z-score")
            
        elif sensor_value > bound[0] :
            print ("The Temperature level increased suddenly. Sending an Email.")
            response = mailer.send_email("Z_Alert_High", "The Current temperature sensor value is " +str(sensor_value))
            print("This is the response ",response)
            
        elif sensor_value < bound[1]:
            print ("The Temperature level decreased suddenly. Sending an Email.")
            response = mailer.send_email("Z_Alert_Low", "The Current temperature sensor value is " +str(sensor_value))
            print("This is the response ",response)
    except Exception as e:
        print ("Error",e)
    time.sleep(10)