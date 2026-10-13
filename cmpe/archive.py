"""Content addressed local/S3 evidence store.

Access control and immutable retention are storage infrastructure responsibilities.
"""
import hashlib,os
from pathlib import Path

def archive_bytes(data:bytes,*,namespace:str="public")->dict:
    if not isinstance(data,bytes) or not data:raise ValueError("nonempty bytes required")
    if namespace not in {"public","economic"}:raise ValueError("invalid namespace")
    digest=hashlib.sha256(data).hexdigest()
    key=f"{namespace}/sha256/{digest[:2]}/{digest}"
    bucket=os.getenv("CMPE_ARCHIVE_BUCKET")
    if bucket:
        import boto3
        from botocore.exceptions import ClientError
        kwargs={}
        if os.getenv("CMPE_ARCHIVE_ENDPOINT"):
            kwargs["endpoint_url"]=os.environ["CMPE_ARCHIVE_ENDPOINT"]
        s3=boto3.client("s3",**kwargs)
        try:
            s3.put_object(Bucket=bucket,Key=key,Body=data,ContentType="application/json",
                          Metadata={"sha256":digest},ServerSideEncryption="AES256",IfNoneMatch="*")
        except ClientError as exc:
            if exc.response.get("Error",{}).get("Code") not in ("412","PreconditionFailed"):
                raise
            metadata=s3.head_object(Bucket=bucket,Key=key)
            if metadata.get("Metadata",{}).get("sha256")!=digest or metadata.get("ContentLength")!=len(data):
                raise RuntimeError("pre-existing object has mismatched digest or size") from exc
        location=f"s3://{bucket}/{key}"
    else:
        root=Path(os.getenv("CMPE_ARCHIVE_DIR","state/archive")); path=root/key
        path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        try:
            with path.open("xb") as f:f.write(data)
        except FileExistsError:
            if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
                raise RuntimeError("pre-existing local object checksum mismatch")
        location=str(path)
    return {"sha256":digest,"location":location,"bytes":len(data)}
