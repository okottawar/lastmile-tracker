import logging, base64
from email.message import EmailMessage
import aiosmtplib
from app.core.config import get_settings
from app.models.enums import OrderStatus

logger=logging.getLogger("notifications")
settings=get_settings()
STATUS_MESSAGES={
 OrderStatus.CREATED:"Your order {order_number} has been created.",OrderStatus.ASSIGNED:"A delivery agent has been assigned to your order {order_number}.",OrderStatus.PICKED_UP:"Your package for order {order_number} has been picked up.",OrderStatus.IN_TRANSIT:"Your order {order_number} is in transit.",OrderStatus.OUT_FOR_DELIVERY:"Your order {order_number} is out for delivery.",OrderStatus.DELIVERED:"Your order {order_number} has been delivered. Thank you!",OrderStatus.FAILED:"Delivery attempt for order {order_number} failed. You can reschedule from your dashboard.",OrderStatus.RESCHEDULED:"Your order {order_number} has been rescheduled.",OrderStatus.CANCELLED:"Your order {order_number} has been cancelled."
}

async def send_email(to_email,subject,body):
    if not settings.SMTP_ENABLED:
        logger.info("[EMAIL disabled] To=%s Subject=%s Body=%s",to_email,subject,body); return False
    try:
        message=EmailMessage(); message["From"]=settings.SMTP_FROM; message["To"]=to_email; message["Subject"]=subject; message.set_content(body)
        await aiosmtplib.send(message,hostname=settings.SMTP_HOST,port=settings.SMTP_PORT,username=settings.SMTP_USER,password=settings.SMTP_PASSWORD,start_tls=True)
        return True
    except Exception as exc:
        logger.error("Failed to send email to %s: %s",to_email,exc); return False

async def send_sms(to_phone,body):
    if not settings.SMS_ENABLED or not to_phone:
        logger.info("[SMS disabled] To=%s Body=%s",to_phone,body); return False
    try:
        import aiohttp
        auth=base64.b64encode(f"{settings.TWILIO_ACCOUNT_SID}:{settings.TWILIO_AUTH_TOKEN}".encode()).decode()
        url=f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
        async with aiohttp.ClientSession() as session:
            async with session.post(url,data={"From":settings.TWILIO_FROM_NUMBER,"To":to_phone,"Body":body},headers={"Authorization":f"Basic {auth}"}) as resp: return resp.status<300
    except Exception as exc:
        logger.error("Failed to send SMS to %s: %s",to_phone,exc); return False

async def notify_status_change(customer_email,customer_phone,order_number,status):
    body=STATUS_MESSAGES.get(status,"Your order {order_number} status is now: "+status.value).format(order_number=order_number)
    await send_email(customer_email,f"Order {order_number} Update: {status.value}",body)
    if customer_phone: await send_sms(customer_phone,body)
