"""Planning capacity model with transparent variables; not a hosting quotation."""
from math import ceil, isfinite

def estimate(reporters:int=10000,records_per_reporter_daily:int=1000,bytes_per_record:int=1024,
             retention_years:int=5,storage_copies:int=3,peak_factor:float=8.0,
             gb_month_usd:float=0.0)->dict:
    if not 1<=reporters<=100_000_000 or not 1<=records_per_reporter_daily<=5_000_000:
        raise ValueError("institution count or event volume out of supported bounds")
    if not 128<=bytes_per_record<=1_000_000 or not 1<=retention_years<=40 or not 1<=storage_copies<=8:
        raise ValueError("size, copies, or retention out of bounds")
    if not isfinite(peak_factor) or not 1<=peak_factor<=100:
        raise ValueError("peak factor out of bounds")
    if not isfinite(gb_month_usd) or gb_month_usd<0 or gb_month_usd>1000:
        raise ValueError("storage unit rate must be finite and nonnegative")
    events=reporters*records_per_reporter_daily
    byte_day=events*bytes_per_record
    bytes_year=byte_day*365
    bytes_retained=bytes_year*retention_years*storage_copies
    gb_month=bytes_retained/(1024**3)
    return {
        "scope":"ingestion/storage only; not compute, audits, analytics, network or disaster recovery",
        "reporting_institutions":reporters,
        "daily_records":events,
        "average_records_per_second":round(events/86400,2),
        "peak_records_per_second":ceil(events/86400*peak_factor),
        "raw_annual_terabytes":round(bytes_year/10**12,3),
        "retained_replica_petabytes":round(bytes_retained/10**15,3),
        "retained_storage_gib":round(gb_month,3),
        "storage_monthly_usd_at_user_rate":round(gb_month*gb_month_usd,2),
        "excludes":["index overhead","warehouse materializations","independent audit labor",
                    "storage transaction pricing","network egress","backups",
                    "source instrumentation","security operations","physical measurement quality"],
        "national_readiness":False,
    }
