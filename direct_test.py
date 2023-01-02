
# THIS FILE CAN ONLY BE USED TO TEST THE CODE IN LOCAL SYSTEM TO PERFORM A QUICK CHECK.

event = {
   "httpMethod":"POST",
   "body":"{\"ETL_PROCESS\":[\"ok\"]}"
}
context = None
from order_reformer_function import app

return_dict = app.lambda_handler(event, context)

print(return_dict)