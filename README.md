OTP Brute-Force Penetration Testing

This project demonstrates controlled penetration testing of OTP-based mobile authentication systems using brute-force attacks in a safe lab environment.

Lab Setup

Attacker Machine: Kali Linux VM.

Target Machine: Windows running a Flask OTP server.

Network: NAT or Bridged connection to allow attacker-target communication.

Test Users: Accounts with pre-configured OTP secrets stored in the server database.

Step-by-Step Methodology

Verify Connectivity

Ensure the Kali VM can reach the OTP server.

Confirm the server responds correctly to valid OTP requests.

Prepare OTP Attack Data

Determine OTP type (TOTP/HOTP) for test users.

Generate sequential or list-based OTP codes for brute-force attempts.

Execute Brute-Force Attack

Submit OTPs using automated tools (Python scripts or Patator).

Track each request with user, OTP attempted, timestamp, and server response.

Monitor server behavior, response times, and failure handling.

Log and Monitor Attempts

Capture all server responses and store logs locally.

Record metrics such as success/failure, latency, and optional uncertainty scores.

Analyze Results

Determine the success rate of brute-force attempts.

Evaluate server responses and rate-limiting mechanisms.

Identify potential weaknesses in OTP implementation.

Risk Assessment

Assess likelihood and impact of each vulnerability.

Prioritize issues based on potential security risk.

Recommendations & Mitigation

Suggest improvements such as:

Stronger OTP randomness

Secure seed storage

Server-side rate limiting or lockouts

Encrypted OTP transmission

Documentation

Record methodology, results, and conclusions.

Include logs and metrics for reproducibility and reference.
