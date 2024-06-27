logging.basicConfig(level=logging.INFO)
 
# Constants
REQUIRED_HEADERS = ["x_agw_api_id", "x-agw-client_id"]
 
 
@dataclass
class MeteringParams:
    request: dict
    r_parent_wf_req_id: str = "NA"
    r_user_id: str = "NA"
    r_param_1: Union[str, list] = "NA"
    r_param_2: dict = field(default_factory=lambda: "NA")
    r_uom_id: int = 0
    r_uom_val: Union[str, list] = 0
    r_vendor_id: Union[int, list] = 0
    additional_params: dict = (
        field(default_factory=dict),
    )  # To hold any additional parameters
