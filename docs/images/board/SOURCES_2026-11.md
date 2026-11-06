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
