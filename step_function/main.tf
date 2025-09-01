# Lambda IAM Role
resource "aws_iam_role" "lambda_role" {
  name = "lambda_retrigger_step_function_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# IAM Policy for Lambda to Start Step Function Execution
resource "aws_iam_policy" "lambda_sfn_policy" {
  name        = "lambda_sfn_start_execution_policy_${random_id.suffix.hex}"
  description = "Allow Lambda to start Step Function execution"
  policy      = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "states:StartExecution"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_sfn_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambda_basic_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda Function
resource "aws_lambda_function" "retrigger_step_function" {
  filename         = "lambda/retrigger_step_function.zip"
  function_name    = "retrigger_step_function"
  role             = aws_iam_role.lambda_role.arn
  handler          = "retrigger_step_function.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = filebase64sha256("lambda/retrigger_step_function.zip")
  timeout          = 60
}

# EventBridge Rule for Step Function Failure
resource "aws_cloudwatch_event_rule" "sfn_failed" {
  name        = "step_function_failed_rule"
  description = "Trigger Lambda on Step Function failure"
  event_pattern = jsonencode({
    "source": ["aws.states"],
    "detail-type": ["Step Functions Execution Status Change"],
    "detail": {
      "status": ["FAILED"]
    }
  })
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.sfn_failed.name
  target_id = "lambda"
  arn       = aws_lambda_function.retrigger_step_function.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.retrigger_step_function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.sfn_failed.arn
}

# Create IAM Role for Step Function 1
resource "aws_iam_role" "step_function_role" {
  name = "step_function_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "states.amazonaws.com"
      }
    }]
  })
}

# Create Step Function State Machine 1
resource "aws_sfn_state_machine" "example" {
  name     = "example-state-machine"
  role_arn = aws_iam_role.step_function_role.arn
  definition = jsonencode({
    Comment = "A Hello World example with failure"
    StartAt = "HelloWorld"
    States = {
      HelloWorld = {
        Type = "Pass"
        Result = "Hello, World!"
        Next = "FailState"
      },
      FailState = {
        Type = "Fail"
        Error = "FailedByDesign"
        Cause = "This state always fails."
      }
    }
  })
}

# Create IAM Role for Step Function 2
resource "aws_iam_role" "step_function_role_2" {
  name = "step_function_role_2"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "states.amazonaws.com"
      }
    }]
  })
}

# Create Step Function State Machine 2
resource "aws_sfn_state_machine" "example_2" {
  name     = "example-state-machine-2"
  role_arn = aws_iam_role.step_function_role_2.arn
  definition = jsonencode({
    Comment = "A second Hello World example with failure"
    StartAt = "HelloWorld2"
    States = {
      HelloWorld2 = {
        Type = "Pass"
        Result = "Hello again, World!"
        Next = "FailState2"
      },
      FailState2 = {
        Type = "Fail"
        Error = "FailedByDesign2"
        Cause = "This state always fails in state machine 2."
      }
    }
  })
}

resource "random_id" "suffix" {
  byte_length = 4
}