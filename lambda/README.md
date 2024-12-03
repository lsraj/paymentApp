# Lambda concepts

Here are the important AWS Lambda concepts that one must know.

## Timeout

Any Lambda function has a defined timeout. That is, the maximum amount of time the Lambda function can run. If it reaches a logical end before that, it’s successful. That means that it terminates the processing and exits with the timeout error.

This timeout is a safety feature to avoid problems if a logical error in the code or an external dependency keeps the code running forever.

The default value of this timeout is three seconds. That’s also the minimum possible value for the timeout. We can specify a higher value for up to 15 minutes.

Whatever the configured timeout value, the Lambda function is billed only for the actual runtime in milliseconds.


## Memory

Lambda memory refers to the RAM available to the code running in the Lambda function. Note that AWS bills us for the RAM provisioned, regardless of the actual usage. That said, we should provide just enough RAM to ensure minimal cost.

We always have a trade-off between the RAM and the execution time. Choking the RAM can increase the computation time, and a generous RAM can make it faster. Therefore, it’s essential to choose the optimal combination of the two to ensure low latency and cost.

## Concurrency

Each account has a maximum limit on the number of Lambda functions that can run simultaneously. However, this limit is soft, and a simple request to AWS can extend it.

By default, the limit is 1000 concurrent Lambda executions. All functions in the account share this limit defined in the account. However, we can reserve part of it for a given Lambda function.
