이미지 조회 api 

curl 'https://api.catchtable.net/api/v3/shop/detail/gallery_the_square?localeCode=en-US' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: ko,en-US;q=0.9,en;q=0.8' \
  -b '_fwb=50mFEkWrVSTcvrKI1IH6Sd.1742877446679; ab180ClientId=2b7cdfb6-0f83-4c24-92c2-a15d693f7d96; tk_ai=6wmS5n%2Bi9AiMF0bEmUM8FEnA; _hackle_hid=9f6bb683-32b6-4a53-aaec-d60b00c63280; _hackle_did_C5tPqwgqb4ifXg88LGrLgf2Hizuhlqfz=9f6bb683-32b6-4a53-aaec-d60b00c63280; _hackle_mkt_C5tPqwgq=%7B%7D; _hackle_did_ogNkJ6yn2WsYE1CgjvdAfXbVJTAbGJnA=9f6bb683-32b6-4a53-aaec-d60b00c63280; _hackle_uid_C5tPqwgqb4ifXg88LGrLgf2Hizuhlqfz=OgL87Q1xnh2xcotGCiWU2Q; _hackle_uid_ogNkJ6yn2WsYE1CgjvdAfXbVJTAbGJnA=sBq4dCCYrhNqyGxv0Mht7Q; _fbp=fb.1.1773039790359.230295551846848953; airbridge_migration_metadata__catchtableglobaldev=%7B%22version%22%3A%221.11.4%22%7D; airbridge_session__catchtableglobaldev=%7B%22id%22%3A%2255f1ced4-a456-40ac-b6b1-dc0dfd5c2631%22%2C%22timeout%22%3A1800000%2C%22start%22%3A1773039791020%2C%22end%22%3A1773041041826%7D; _ga=GA1.1.334478457.1762507160; _ga_9ENCGJ7C7P=GS2.1.s1773142813$o1232$g0$t1773142813$j60$l0$h0; _hackle_session_id_b4ifXg88LGrLgf2Hizuhlqfz=1773143796975.da53c0dd; airbridge_migration_metadata__catchtableglobalstg=%7B%22version%22%3A%221.11.4%22%7D; airbridge_session__catchtableglobalstg=%7B%22id%22%3A%22221e7ecd-466a-444a-8cbf-ab78a02fe375%22%2C%22timeout%22%3A1800000%2C%22start%22%3A1773143797598%2C%22end%22%3A1773143797598%7D; _hackle_last_event_ts_b4ifXg88LGrLgf2Hizuhlqfz=1773143798224; _gcl_au=1.1.1135637580.1773310529; _hackle_mkt_ogNkJ6yn=%7B%7D; airbridge_migration_metadata__catchtableglobal=%7B%22version%22%3A%221.11.5%22%7D; _hackle_session_id_2WsYE1CgjvdAfXbVJTAbGJnA=1774233140144.4180d6f5; airbridge_session__catchtableglobal=%7B%22id%22%3A%22c92b0a04-a319-4346-9282-30156c40cd6a%22%2C%22timeout%22%3A1800000%2C%22start%22%3A1774233922306%2C%22end%22%3A1774234002544%7D; JSESSIONID=FE118D7E0528567FA8FC7733AA0E4409; __cf_bm=xEmTlwc0LpEXjdC9fzSgEnnfHFiJiE3Yp5yxhXrXFPo-1774234051.0764208-1.0.1.1-eohQORwxDQI9qETCm1ebj1IIH5gANkndl8jMbKVEhbeXZCt6xlewh7jiMjvvvhAJ2UOYP_HhOn2nOtG9Hv08zG4XwvODIZAi7d5fZiMGJZub.VveyTJReI6GLNFUL9h9; x-ct-a=AABrcmFweXMAAAAHAG1uAgBCAAAAAgBwYQICJroSAHF1YxABFwRYAHF1EAAAbm9pc3JlVnNvSXRzZXdlTnNpCABHAAAAAgBwYWwCAEcAAAACAHRqAgAuLmtyYXB5cwAAAAkAbmQCAAABnR29fkUAdEFweGUSAGRvcnAAAAAFAHBsAgBTVS1uZQAAAAYAbmwCAHBwCgAAAJgCOkqJb7uNW0GmSBSKOUWbW4Xmck=; _ga_XTCBJKH3ZM=GS2.1.s1774233140$o460$g1$t1774234051$j10$l0$h0; _hackle_last_event_ts_2WsYE1CgjvdAfXbVJTAbGJnA=1774234051124' \
  -H 'origin: https://www.catchtable.net' \
  -H 'priority: u=1, i' \
  -H 'sec-ch-ua: "Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"' \
  -H 'sec-ch-ua-mobile: ?1' \
  -H 'sec-ch-ua-platform: "iOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1' \
  -H 'x-transaction-id: 9'

  응답형태 

  {
    "resultCode": "CT_OK",
    "displayMessage": null,
    "message": null,
    "data": {
        "latestReservationRegDate": 1774190650000,
        "hiddenWeeklyButtonInfo": null,
        "shopDisableDays": [],
        "lightPeriodList": [],
        "shopOpenScheduleList": [],
        "shopDetails": [
            {
                "shopRef": "F-qIOt1O0ZINOEG9jqREYw",
                "alias": "gallery_the_square",
                "shopName": "갤러리 더 스퀘어 계동점",
                "shopNameEn": "Gallery, The Square, Gye-dong",
                "images": [
                    {
                        "thumbUrl": "https://ugc-images.catchtable.co.kr/catchtable/shopinfo/sF-qIOt1O0ZINOEG9jqREYw/m/78a9f67d0b7b4ca3b1e709d786a17b6a",
                        "imgUrl": "https://ugc-images.catchtable.co.kr/catchtable/shopinfo/sF-qIOt1O0ZINOEG9jqREYw/m/78a9f67d0b7b4ca3b1e709d786a17b6a",
                        "imgWidth": 1000,
                        "imgHeight": 1334,
                        "videoUrl": null,
                        "videoWidth": 0,
                        "videoHeight": 0,
                        "video": false
                    }
                ],
                
                ... 생략 ...
    }
}

위 응답의 data.shopDetails.images.thumbUrl 이 매장 메인 이미지야.
https://api.catchtable.net/api/v3/shop/detail/gallery_the_square

의  gallery_the_square 는 catchtable_url_path (tablenote.tn_shop_master 테이블) 이고 slug 개념의 값이야.

