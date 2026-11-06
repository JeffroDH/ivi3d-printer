# Board photo sources (2026-11)

Owner photos of the IVI main board, EXIF/GPS stripped where applicable.
No printer serial numbers are intentionally included. Chip date/lot codes and the board
design marking `A33_407MB_200916` are not printer serials.

## Chassis / exposed-for-inspection set

| File | Subject | Source attachment |
|---|---|---|
| front_overview_2026-11.jpg | Front overview | 01M6Q0W8MN8N866J4GB4GXWPHV (cropped) |
| front_som_chips.jpg | SoM chip markings | 01M6Q0VBSVYBZTMB95DJG1QDRT |
| front_stm32_swd.jpg | STM32F407VET6 + SWD | 01M6Q0VBSVYBZTMB95DJG1QDRT |
| front_sd_3pin_usb.jpg | microSD / 3-pin / micro-USB | 01M6Q0VBSVYBZTMB95DJG1QDRT |
| front_fivepin_soic16.jpg | Bottom-left 5-pin + SOIC-16 (pre-ID crop) | parent crop from 01M6Q0W8… |
| front_fivepin_ch340g.jpg | CH340G by 5-pin (rotated macro) | uart-five-pin-crop / front macros |
| front_wifi_module.jpg | Shielded RF module AP6236 | 01M6Q0GJPVN9TP9X344CK0BKS1 |
| rear_board_marking.jpg | Rear design silk | 01M6PZVS3B5KEW8Y84KWE2X87Y |
| rear_debuguart_pads.jpg | DEBUGUART_RX/TX/GND | 39805f47… / 01M6Q00CCR8VV19ZD4M34TXRM8 ruler photo |

## Removed-on-wood still set (later 2026-11-05)

Board photographed on a wood surface (removed from chassis for this set). Local working copies hashed below; attachment id prefixes from the chat drop.

| File | Subject | Source still (local / id prefix) |
|---|---|---|
| front_removed_wood_overview.jpg | Full front on wood | e1e… (sha256 fb4116063940…) |
| front_amass_power.jpg | Amass brand yellow 3-pin inlet | e1e… crop |
| front_power_amass_pptc.jpg | Amass + PPTC / electrolytics | e1e… crop |
| front_usb_ch340_ssop_zone.jpg | CH340G + GL850G SSOP zone | 7d2… crop |
| front_ch340g_wood.jpg | CH340G close | 7d2… crop |
| front_ssop_near_ch340.jpg | GL850G SSOP close | 7d2… crop |
| front_rf_kapton_wires.jpg | AP6236 area / Kapton / black wires | 907… crop |
| front_bottom_kapton_wires.jpg | Bottom Kapton / wire area | e1e… crop |

| Local still | Size | sha256 (12) |
|---|---|---|
| e1e.jpg | 3024×4032 | fb4116063940 |
| 907.jpg | 3024×4032 | 08d929b2fd15 |
| 7d2.jpg | 3024×4032 | 59137a5f1609 |

**Video:** a `.mov` from this session was present in chat but **not analyzed** (shell/`watchVideo` could not access the attachment). No content is inferred from any thumbnail. Reattach if video findings are needed.

Earlier board photos (`mainboard_*.jpg`) remain from 2026-10-31.


## Evening JPEG set (2026-11-05, later)

Held-board front/rear/edge/antenna JPEGs. Hash names under agent `attachments/` were not always visible to Shell; files were recovered from the cursor store batch `01M6Q8D*` (19:43 America/Chicago), EXIF-stripped copies under `/workspace/ivi-board-raw/nov5-evening/`.

| Repo file | Subject | Notes |
|---|---|---|
| front_3pin_rx_tx_gnd.jpg | Front 3-pin silk RX/TX/GND | From store `01M6Q8DKX25…` / hash bb713… |
| rear_debuguart_gnd_rx_tx.jpg | Rear GND → DEBUGUART_RX → DEBUGUART_TX | Crop from rear still `01M6Q8DFED…` |
| front_ap6236_kapton_antenna_feed.jpg | AP6236 + Kapton coax attach | Front evening |
| side_flat_external_antenna.jpg | Flat external antenna + coax | Side view |
| edge_power_connector_row.jpg | Power-row edge (Amass + white headers) | Edge view |
| edge_view_d8b.jpg | Opposite edge / antenna leave | Edge view |
| front_overview_2026-11-evening.jpg | Front overview | Evening |
| rear_overview_2026-11-evening.jpg | Rear overview | Evening |

**Not analyzed:** session video; DNG raws (paths not materialized for tools).


## Motor / display / edge-board photos (2026-11-05, later)

Claimed attachment hashes (`e8ce01d0…` motor, `d39f4fa4…` display back, `8a93a3a7…` flex macro, `db2820e3…` small-board macro) were **not present** for Shell/Read when documented. No images were copied into this folder for that set. Narrative evidence is in [motors_and_display.md](../../motors_and_display.md) tagged **[Pᵗ]** (parent-transcribed). Re-archive here when files are available (strip EXIF/GPS; no printer serials).


## IC close-up set (2026-11-06)

Owner stated close-ups of most ICs were attached (nine JPEGs). At documentation/push time those attachment hashes were **not readable** by agent tools and were not newly present in the cursor store. No additional crops were committed from that drop (hashes still missing for tools). Parent-visible inventory (A33 die, AP6236 **B112A015**, NP1404 SOIC-8s, etc.) is in [mainboard.md](../../mainboard.md) §6d tagged **[Pᵗ]** — **local/unpushed** relative to the A33 docs push unless separately approved.


## 2026-11-06 16-file reupload

Hashes listed in the agent task (extruder×3, motor, rear QFN, NP1404×n, AXP223, eMMC, A33, CH340/GL850G, GL850G). Parent Read of first path succeeded; **executor staged 0/16** into `/workspace/ivi-board-recovered/nov6-reupload/` this pass. Critical marking update from parent: USB-UART IC reads **CH340C** (not G). No GPS/serial-bearing binaries committed.


| front_ch340c_gl850g_2026-11-06.jpg | CH340C + GL850G overview | `503fbbb7…` reupload (EXIF stripped) |
| front_ch340c_marking.jpg | CH340C top mark crop | same |
| front_gl850g_marking.jpg | GL850G top mark crop | same |

Executor recovery **1/16** of the Nov 6 reupload set; see `/workspace/ivi-board-recovered/nov6-reupload/ACCESS.md` for the 15 missing hashes.


| front_a33_die_marking.jpg / front_a33_overview_2026-11-06.jpg | A33 die | `902e9745…` |
| front_np14p04_marking.jpg | NP14P04 SOIC-8 | `1fdade3f…` |
| front_axp223_2026-11-06.jpg | AXP223 | `e9ed08f3…` |
| front_emmc_2026-11-06.jpg | eMMC | `59c3e7e4…` |
| front_power_converter_2026-11-06.jpg | Power SOP-8 | `a6945446…` |

Full 16-file set: `/workspace/ivi-board-recovered/nov6-reupload/originals/` (all 3024×4032).

## 2026-11-06 rear-debug / USB context (EXIF stripped)

| File | Notes |
|---|---|
| `rear_chip_close.jpg` | Owner rear closeup of bottom-right MCU area; EXIF/GPS stripped. Marking **E230F4** / GigaDevice **G** / lot **JJ2014** → **GD32E230F4** **[P]**. |
| `gd32e230f4_chip_close_crop.jpg` | Crop from `rear_chip_close.jpg`, rotated upright; **Read-verified** before embed (shows chip face, not nearby passives). Prior wrong “upright” crop that showed only passives was **not** committed. |
| `microusb_clear.jpg` | Clearer micro-USB context photo only. **No pad-annotation overlays** (earlier annotated boxes had bad offsets and are **not** used). USB D± photo-routing claims retracted. |

Confidence: chip ID **[P]** + family datasheet **[D]**; lower-SWD ↔ rear pads **[O]**; chip↔header nets **[U]**.

