# HSPNT01 | VM capability scenario (public, preparatory)

**State:** PREPARED_ONLY / NOT_DISPATCHED / VM_NOT_CREATED / NO_GO_OPERATIONAL.
**Repository:** jorgemunizoficial/lab-runner-validation.
**Owner:** HSPRB01 (baseline planning), under HSPVD01 Order 001 v2.0 and PO authorization to prepare only.
**Source of requirements:** H-VMS/hvms-security-all-platform, order commit 40904289ae2b96069e6c67f3a0d415fa7a6d3895.
**Baseline:** H-VMS/hvms-provisioning-baselines commit c5393fc5689f3a1c18aafef4b8cc10837e2a5dcf.

## Purpose and boundaries
This scenario asks whether a standard GitHub-hosted `ubuntu-24.04` runner exposes the *prerequisites* needed to consider nested KVM. It does not create a VM, install KVM/libvirt, download images, execute HSPNT01 code, connect to any network endpoint, or establish a dedicated VM. It makes no claim that nested virtualization is supported or that the host can provide persistent dedicated resources.

Public GitHub repo: **no H-VMS private code, customer data, real IPs, secrets, private checkout or private URLs**. No artifacts/caches, no third-party Actions. Existing workflows and `main` remain unchanged. This scenario is a separate manually dispatched workflow on a feature branch; merging into `main` is not authorized.

## One future workflow
`.github/workflows/hspnt01-dedicated-vm-capability.yml` uses `workflow_dispatch`, `contents: read`, a 5-minute timeout, no checked-out repository, and only read-only commands: uname, nproc, /proc/meminfo, df, /sys/fs/cgroup/cgroup.controllers, /dev/kvm existence, systemd-detect-virt, executable availability. No privileged calls, curl, sudo, container, VM, network probe, image download or host mutation.

**No workflow_dispatch authorization is given here.** Future dispatch requires a new explicit PO decision *for the run*, CISO review, a documented outside observer/evidence custodian, cost/billing confirmation and full `docs/public-synthetic/PRE-DISPATCH-STATIC-GATE.md`. This repository is public and its logs must remain sanitized.

## Mapping to P01–P08
| Gate | What this scenario can establish once authorized and run | What remains NOT_PROVEN |
|---|---|---|
| P01 | Ephemeral runner metadata/capability clues | Dedicated host identity/ownership; custodians; extra costs |
| P02 | CPU/memory/free disk snapshot; QEMU/virsh binary presence | Real guest 2vCPU/2GiB/8GiB, official guest image checksum, reproducibility, nested KVM |
| P03 | Nothing about OS worker/controller/collector isolation | Separate accounts/IPC/root/broker and canaries |
| P04 | Nothing about guest filesystems/evidence anchors | Quotas, store permissions, immutable evidence |
| P05 | Nothing about guest network deny | No-NIC effective guest network policy, IPv4/IPv6/DNS/metadata denial |
| P06 | Cgroup v2 controller visibility only | Delegation/effective limits, 2 jobs, 30s, 5s, 4KiB output, 16MiB job |
| P07 | No recovery state | Actual VM crash/rebuild, orphan cleanup and preservation |
| P08 | Run metadata available when executed | independent CISO acceptance, HSPNT01 A01-A08 and L01-L03 |

**Key distinction:** a GitHub Actions hosted runner is already a temporary VM. Container tests previously passed in this repo, but Docker isolation is not equivalent to a nested dedicated VM. A successful capability workflow would be evidence only of the read-only inventory, not KVM compatibility or operational security.

## Next decision
After independent review of this branch, PO may authorize a single read-only capability dispatch. Depending on evidence, choose either (A) a separately approved VM environment that satisfies P01–P08 or (B) limited synthetic Docker tests with explicit CISO exceptions, never automatic substitution of P01–P08.
