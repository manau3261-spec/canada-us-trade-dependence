"""Check real production-server CSV responses. Set the local URL as the argument."""
from argparse import ArgumentParser
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests
from streamlit.proto.BackMsg_pb2 import BackMsg
from streamlit.proto.ForwardMsg_pb2 import ForwardMsg
from websockets.sync.client import connect


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("url", help="URL of a running loopback Streamlit application")
    base = parser.parse_args().url.rstrip("/")
    for path, media in (("/", "text/html"), ("/favicon.png", "image/png")):
        asset = requests.get(base + path, timeout=10)
        assert asset.status_code == 200 and asset.headers["Content-Type"].startswith(media), path
    response = requests.get(f"{base}/_stcore/health", timeout=10)
    assert response.status_code == 200 and response.text == "ok"
    with connect(base.replace("http://", "ws://", 1) + "/_stcore/stream", origin=base,
                 subprotocols=["streamlit"], open_timeout=10) as sock:
        msg = BackMsg()
        msg.rerun_script.SetInParent()
        sock.send(msg.SerializeToString())
        urls = []
        while True:
            reply = ForwardMsg.FromString(sock.recv(timeout=20))
            if reply.HasField("delta") and reply.delta.new_element.HasField("download_button"):
                urls.append(reply.delta.new_element.download_button.url)
            if reply.HasField("script_finished"):
                assert int(reply.script_finished) == 0
                break
        assert len(urls) == 1, urls
        data = requests.get(base + urls[0], timeout=10)
        assert data.status_code == 200 and data.headers["Content-Type"].startswith("text/csv")
        assert data.headers["Content-Disposition"] == 'attachment; filename="national_annual_2010_2025.csv"'
        actual = pd.read_csv(BytesIO(data.content), dtype={"period":str})
        reference = pd.read_csv(Path(__file__).resolve().parents[1] / "data/phase3/annual_exposure.csv",
                                dtype={"period":str}).query("geo=='Canada' and product=='TOTAL'")
        expected = reference[actual.columns].sort_values("period").reset_index(drop=True)
        assert len(actual) == 16
        pd.testing.assert_frame_equal(actual, expected, check_dtype=False)
    print("HTTP 200 index, favicon, health and CSV | UTF-8 attachment | 16 rows | exact values and column order | no credentials")


if __name__ == "__main__":
    main()
