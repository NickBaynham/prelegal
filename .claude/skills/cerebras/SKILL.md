---
name: cerebras
description: Use the Cerebras skill to make calls to the openrouter/openai/gpt-oss-120b model via OpenRouter using the cerebras inference provider.
---

# Calling an LLM with the Cerebras Skill

These instructions will guide you on how to use the Cerebras skill to make calls to the openrouter/openai/gpt-oss-120b model via OpenRouter with cerebras as the inference provider.

# Setup Instructions
To set up the Cerebras skill in your project, follow these steps:

The OPENROUTER_API_KEY environment variable must be set in .env to allow your OpenRouter API key. You can obtain an API key by signing up for an account on the OpenRouter website and creating a new API key in the dashboard. This environment variable must be loaded in your development environment for the Cerebras skill to function properly. Make sure to keep your API key secure and do not share it publicly.

The pdm project in the backend/ directory should have the cerebras package added as a dependency. You can do this by running the following command in the backend/ directory:

```bash
pdm add litellm pydantic
``` 
This will install the Cerebras package and allow you to use the Cerebras skill in your backend code. Make sure to also include any necessary imports in your code where you intend to use the Cerebras skill.


## Step 1: Import the Cerebras Skill

First, you need to import the Cerebras skill into your project. You can do this by adding the following line to your code:

```from litellm import completion
   MODEL = "openrouter/openai/gpt-oss-120b"
   EXTRA_BODY = {"provider": {"order": ["cerebras"]}}
``` 
## Step 2: Make a Call to the LLM
Now you can use the `client` to make a call to the gpt-oss-120b model. You can use the `generate` method to send a prompt and receive a response from the model. Here's an example:

```response = completion(
    model=MODEL,
    messages=messages,
    reasoning_effort="low",
    extra_body=EXTRA_BODY
  )
  result = response.choices[0].message.content
``` 

## Step 3: Handle the Response with Structured Output
When making a call to the LLM, you can specify that you want the output to be structured. This means that the response will be in a format that can be easily parsed and used in your application. To enable structured output, you can set the `structured_output` parameter to `True` when making the call. Here's an example:

```response = completion(
    model=MODEL,
    response_format=MyBassModelSubclass,
    messages=messages,
    reasoning_effort="low",
    extra_body=EXTRA_BODY,
    structured_output=True
  )
  result = response.choices[0].message.content
  result_as_object = MyBassModelSubclass.model_validate_json(result)
```

## Conclusion
By following these steps, you can successfully use the Cerebras skill to make calls to the openrouter/openai/gpt-oss-120b model via OpenRouter with cerebras as the inference provider. Remember to always check the documentation for any additional parameters or options you can use when making calls to the LLM.
