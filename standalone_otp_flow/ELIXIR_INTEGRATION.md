# PSA OTP - Elixir Integration Guide

This guide shows how to call the PSA OTP flows from Elixir.

## Overview

Two standalone Python scripts for OTP flow:

1. **otp_setup.py** - Initial setup (receives SMS code, creates session)
2. **otp_generate.py** - Generate OTP code (reads session, outputs code)

Both scripts are designed to be called from Elixir using `System.cmd/3`.

## Prerequisites

```bash
# Install Python dependencies (in venv)
cd standalone_otp_flow
python3 -m venv venv
source venv/bin/activate
pip install pycryptodomex requests
```

## Script 1: OTP Setup

### Purpose
Creates OTP session file (otp.bin) using SMS code and PIN.

### Command Line Usage

```bash
python otp_setup.py <sms_code> <pin_code>
```

**Example:**
```bash
python otp_setup.py 123456 1234
```

### Output

**Success:**
```
SUCCESS
DEVICE_ID:a1b2c3d4e5f6g7h8
SESSION_FILE:otp.bin
```

**Error:**
```
ERROR: Invalid SMS code
```

### Exit Codes
- `0` - Success
- `1` - Error

### Elixir Integration

```elixir
defmodule PSA.OTP do
  @otp_dir "/path/to/standalone_otp_flow"
  @python_bin "#{@otp_dir}/venv/bin/python"
  @setup_script "#{@otp_dir}/otp_setup.py"

  @doc """
  Setup OTP session with SMS code and PIN

  Returns:
    {:ok, device_id} on success
    {:error, reason} on failure
  """
  def setup(sms_code, pin_code) do
    case System.cmd(@python_bin, [@setup_script, sms_code, pin_code],
                    cd: @otp_dir,
                    stderr_to_stdout: true) do
      {output, 0} ->
        # Parse output
        lines = String.split(output, "\n", trim: true)

        case Enum.at(lines, 0) do
          "SUCCESS" ->
            device_id = lines
                       |> Enum.find(&String.starts_with?(&1, "DEVICE_ID:"))
                       |> String.replace("DEVICE_ID:", "")

            {:ok, device_id}

          _ ->
            {:error, "Setup failed: #{output}"}
        end

      {error_output, _exit_code} ->
        error_msg = error_output
                   |> String.split("\n")
                   |> Enum.find(&String.starts_with?(&1, "ERROR:"), "Unknown error")
                   |> String.replace("ERROR: ", "")

        {:error, error_msg}
    end
  end
end
```

**Usage in Elixir:**
```elixir
# Setup OTP session
case PSA.OTP.setup("123456", "1234") do
  {:ok, device_id} ->
    IO.puts("OTP session created. Device: #{device_id}")

  {:error, reason} ->
    IO.puts("Setup failed: #{reason}")
end
```

## Script 2: OTP Generate

### Purpose
Generates 6-character OTP code from existing session.

### Command Line Usage

```bash
python otp_generate.py [session_file]
```

**Examples:**
```bash
# Use default otp.bin
python otp_generate.py

# Specify custom session file
python otp_generate.py /path/to/otp.bin
```

### Output

**Success:**
```
a3k9m2
```
(Just the OTP code, nothing else)

**Error:**
```
ERROR: Session file not found: otp.bin
```

### Exit Codes
- `0` - Success
- `1` - Error

### Elixir Integration

```elixir
defmodule PSA.OTP do
  @otp_dir "/path/to/standalone_otp_flow"
  @python_bin "#{@otp_dir}/venv/bin/python"
  @generate_script "#{@otp_dir}/otp_generate.py"
  @session_file "#{@otp_dir}/otp.bin"

  @doc """
  Generate OTP code from existing session

  Returns:
    {:ok, otp_code} on success (otp_code is 6-character string)
    {:error, reason} on failure
  """
  def generate(session_file \\ @session_file) do
    case System.cmd(@python_bin, [@generate_script, session_file],
                    cd: @otp_dir,
                    stderr_to_stdout: true) do
      {output, 0} ->
        otp_code = output |> String.trim()

        if String.length(otp_code) == 6 do
          {:ok, otp_code}
        else
          {:error, "Invalid OTP code format: #{otp_code}"}
        end

      {error_output, _exit_code} ->
        error_msg = error_output
                   |> String.split("\n")
                   |> Enum.find(&String.starts_with?(&1, "ERROR:"), "Unknown error")
                   |> String.replace("ERROR: ", "")

        {:error, error_msg}
    end
  end
end
```

**Usage in Elixir:**
```elixir
# Generate OTP code
case PSA.OTP.generate() do
  {:ok, otp_code} ->
    IO.puts("OTP Code: #{otp_code}")

  {:error, reason} ->
    IO.puts("Generation failed: #{reason}")
end
```

## Complete Elixir Module Example

```elixir
defmodule PSA.OTP do
  @moduledoc """
  PSA OTP integration for Elixir

  Calls standalone Python scripts to handle OTP flow.
  """

  @otp_dir "/path/to/psa_car_controller/standalone_otp_flow"
  @python_bin "#{@otp_dir}/venv/bin/python"
  @setup_script "#{@otp_dir}/otp_setup.py"
  @generate_script "#{@otp_dir}/otp_generate.py"
  @session_file "#{@otp_dir}/otp.bin"

  @doc """
  Setup OTP session with SMS code and PIN

  ## Parameters
    - sms_code: SMS code received from PSA (string)
    - pin_code: User's PIN code (string, digits only)

  ## Returns
    - {:ok, device_id} on success
    - {:error, reason} on failure

  ## Example
      iex> PSA.OTP.setup("123456", "1234")
      {:ok, "a1b2c3d4e5f6g7h8"}
  """
  def setup(sms_code, pin_code) when is_binary(sms_code) and is_binary(pin_code) do
    case System.cmd(@python_bin, [@setup_script, sms_code, pin_code],
                    cd: @otp_dir,
                    stderr_to_stdout: true) do
      {output, 0} ->
        parse_setup_output(output)

      {error_output, _exit_code} ->
        {:error, extract_error_message(error_output)}
    end
  end

  @doc """
  Generate OTP code from existing session

  ## Parameters
    - session_file: Path to OTP session file (optional, defaults to otp.bin)

  ## Returns
    - {:ok, otp_code} on success (otp_code is 6-character string)
    - {:error, reason} on failure

  ## Example
      iex> PSA.OTP.generate()
      {:ok, "a3k9m2"}
  """
  def generate(session_file \\ @session_file) do
    case System.cmd(@python_bin, [@generate_script, session_file],
                    cd: @otp_dir,
                    stderr_to_stdout: true) do
      {output, 0} ->
        parse_generate_output(output)

      {error_output, _exit_code} ->
        {:error, extract_error_message(error_output)}
    end
  end

  @doc """
  Check if OTP session exists

  ## Returns
    - true if session file exists
    - false otherwise
  """
  def session_exists?(session_file \\ @session_file) do
    File.exists?(session_file)
  end

  # Private functions

  defp parse_setup_output(output) do
    lines = String.split(output, "\n", trim: true)

    case Enum.at(lines, 0) do
      "SUCCESS" ->
        device_id = lines
                   |> Enum.find(&String.starts_with?(&1, "DEVICE_ID:"))
                   |> String.replace("DEVICE_ID:", "")

        {:ok, device_id}

      _ ->
        {:error, "Setup failed: #{output}"}
    end
  end

  defp parse_generate_output(output) do
    otp_code = String.trim(output)

    if String.length(otp_code) == 6 do
      {:ok, otp_code}
    else
      {:error, "Invalid OTP code format: #{otp_code}"}
    end
  end

  defp extract_error_message(error_output) do
    error_output
    |> String.split("\n")
    |> Enum.find(&String.starts_with?(&1, "ERROR:"), "Unknown error")
    |> String.replace("ERROR: ", "")
  end
end
```

## Usage Examples

### First Time Setup

```elixir
# User receives SMS code from PSA
sms_code = "123456"
pin_code = "1234"

case PSA.OTP.setup(sms_code, pin_code) do
  {:ok, device_id} ->
    # Session created successfully
    # otp.bin file is now available
    IO.puts("Setup complete. Device ID: #{device_id}")

  {:error, reason} ->
    IO.puts("Setup failed: #{reason}")
end
```

### Generate OTP Code

```elixir
# Check if session exists
if PSA.OTP.session_exists?() do
  # Generate OTP code
  case PSA.OTP.generate() do
    {:ok, otp_code} ->
      # Use OTP code for remote access token
      IO.puts("OTP: #{otp_code}")

    {:error, reason} ->
      IO.puts("Failed: #{reason}")
      # Session may have expired, need to run setup again
  end
else
  IO.puts("No OTP session. Run setup first.")
end
```

### Complete Flow

```elixir
defmodule MyApp.PSAAuth do
  alias PSA.OTP

  def get_otp_code() do
    cond do
      # Check if session exists
      OTP.session_exists?() ->
        # Generate OTP from existing session
        case OTP.generate() do
          {:ok, code} -> {:ok, code}
          {:error, _} -> setup_new_session()
        end

      # No session, need setup
      true ->
        setup_new_session()
    end
  end

  defp setup_new_session() do
    # Request SMS from PSA (via your app logic)
    {:ok, sms_code} = request_sms_from_psa()

    # Get PIN from user
    pin_code = get_user_pin()

    # Setup OTP session
    case OTP.setup(sms_code, pin_code) do
      {:ok, _device_id} ->
        # Now generate OTP
        OTP.generate()

      {:error, reason} ->
        {:error, reason}
    end
  end
end
```

## Error Handling

### Common Errors

**Setup Errors:**
- `ERROR: Invalid arguments` - Wrong number of arguments
- `ERROR: SMS code is required` - Empty SMS code
- `ERROR: PIN code must be numeric` - Non-numeric PIN
- `ERROR: Configuration error` - Invalid SMS code or expired
- `ERROR: Failed to create OTP session` - Network or API error

**Generate Errors:**
- `ERROR: Session file not found` - No otp.bin file, run setup first
- `ERROR: Failed to load OTP session` - Corrupted otp.bin
- `ERROR: Configuration error` - Expired session, run setup again
- `ERROR: Failed to generate OTP code` - Network or API error

### Elixir Error Handling Example

```elixir
def handle_otp_error({:error, reason}) do
  cond do
    String.contains?(reason, "Session file not found") ->
      # Need to run setup
      {:needs_setup, "No OTP session found"}

    String.contains?(reason, "expired") ->
      # Session expired, need new setup
      {:needs_setup, "OTP session expired"}

    String.contains?(reason, "Configuration error") ->
      # Invalid SMS or expired
      {:invalid_sms, reason}

    true ->
      # Unknown error
      {:error, reason}
  end
end
```

## Rate Limits

**PSA OTP Limits:**
- Maximum 6 OTP codes per 24 hours
- Handle this in your Elixir app:

```elixir
defmodule PSA.OTPRateLimit do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{count: 0, reset_at: nil}, name: __MODULE__)
  end

  def can_generate?() do
    GenServer.call(__MODULE__, :can_generate?)
  end

  def record_generation() do
    GenServer.cast(__MODULE__, :record)
  end

  # Implementation...
end
```

## Testing

### Test Setup

```bash
cd standalone_otp_flow

# Test setup
python otp_setup.py 123456 1234
# Should output: SUCCESS

# Test generate
python otp_generate.py
# Should output: 6-character code
```

### Elixir Tests

```elixir
defmodule PSA.OTPTest do
  use ExUnit.Case
  alias PSA.OTP

  test "setup with valid SMS and PIN" do
    # Mock or use test credentials
    assert {:ok, _device_id} = OTP.setup("123456", "1234")
  end

  test "generate OTP code" do
    # Assumes session exists
    assert {:ok, code} = OTP.generate()
    assert String.length(code) == 6
  end

  test "session_exists? returns boolean" do
    assert is_boolean(OTP.session_exists?())
  end
end
```

## Deployment

### Directory Structure

```
your_elixir_app/
├── lib/
│   └── psa/
│       └── otp.ex           # Elixir module
├── priv/
│   └── psa_otp/             # Python scripts
│       ├── venv/            # Python virtual environment
│       ├── otp_setup.py
│       ├── otp_generate.py
│       ├── otp.py
│       ├── load.py
│       ├── tokenizer.py
│       ├── oaep.py
│       └── otp.bin          # Created at runtime
```

### Setup in Production

```bash
# In your deployment script
cd priv/psa_otp
python3 -m venv venv
source venv/bin/activate
pip install pycryptodomex requests
```

### Environment Variables

```elixir
# In config/runtime.exs
config :my_app, PSA.OTP,
  otp_dir: System.get_env("PSA_OTP_DIR", "/app/priv/psa_otp"),
  python_bin: System.get_env("PSA_PYTHON_BIN", "/app/priv/psa_otp/venv/bin/python")
```

## Security Considerations

1. **Session File Protection**
   - `otp.bin` contains sensitive encryption keys
   - Store with restricted permissions (600)
   - Don't commit to version control

2. **PIN Code Security**
   - Never log PIN codes
   - Clear from memory after use
   - Consider encryption at rest

3. **Rate Limiting**
   - Implement rate limiting in Elixir
   - Track OTP generations (max 6/24h)

## Troubleshooting

### Python not found
```elixir
# Check Python path
System.cmd("which", ["python3"])
```

### Import errors
```bash
# Ensure dependencies installed in venv
cd standalone_otp_flow
source venv/bin/activate
pip list | grep pycryptodomex
```

### Permission errors
```bash
# Make scripts executable
chmod +x otp_setup.py otp_generate.py
```

### Session file issues
```bash
# Check file exists and is readable
ls -la otp.bin
file otp.bin
```

## Support

For issues:
1. Check exit codes (0 = success, 1 = error)
2. Read stderr output for error messages
3. Verify Python dependencies installed
4. Check file permissions
5. Review PSA rate limits

## Quick Reference

**Setup:**
```bash
python otp_setup.py <sms_code> <pin_code>
```

**Generate:**
```bash
python otp_generate.py [session_file]
```

**Elixir:**
```elixir
PSA.OTP.setup(sms_code, pin_code)  # {:ok, device_id} | {:error, reason}
PSA.OTP.generate()                  # {:ok, otp_code} | {:error, reason}
PSA.OTP.session_exists?()           # true | false
```
