from tonic_textual.api import TonicTextual

tonic_api_key=""
textual = TonicTextual("https://textual.tonic.ai", tonic_api_key)

redacted_text = textual.redact("""The IP 192.168.123.132 has breached our
firewall. The machine is registered to a man named Luke McFee, a US Citizen
in Japan. This is a clear violation of The Computer Fraud and Abuse Act.""")

#This returns an object including the redact text and metadata.
print(redacted_text.redacted_text)