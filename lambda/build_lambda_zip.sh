#
# Run this from the dir where lambda_function.py is
#

pip install -r requirements.txt -t package/
cp lambda_function.py package/
cd package && zip -r9 ../paymentApp-lambda.zip . && cd ..
rm -rf package
