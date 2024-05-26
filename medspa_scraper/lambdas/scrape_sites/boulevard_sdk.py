import requests
from typing import Dict


def auth_boulevard(headers: Dict[str, str], location_id: str, email: str):
    json_data = {
        "query": "\n  mutation CreateCart($locationId: ID!, $email: Email) {\n    createCart(locationId: $locationId, cart: { clientInformation: { email: $email }}) {\n      cartToken: cartToken\n    }\n  }\n",
        "variables": {
            "locationId": location_id,
            "email": email,
        },
    }

    response = requests.post(
        "https://dashboard.boulevard.io/api/v1.0/graph_client",
        headers=headers,
        json=json_data,
    )
    return response.json()


def get_procedure_ids(headers: Dict[str, str], cart_id: str):
    json_data = {
        "query": "\n  query GetMenuItems($cartId: ID!) {\n    cart(idOrToken: $cartId) {\n      availableCategories {\n        disabled\n        disabledDescription\n        name\n      }\n    }\n  }\n",
        "variables": {"cartId": cart_id},
    }

    response = requests.post(
        "https://dashboard.boulevard.io/api/v1.0/graph_client",
        headers=headers,
        json=json_data,
    )
    return response.json()


def get_patient_type(headers: Dict[str, str], cart_id: str):
    json_data = {
        "query": "\n  query GetMenuCategory($cartId: ID!) {\n    cart(idOrToken: $cartId) {\n      availableCategories {\n        name\n        availableItems {\n          id\n          disabled\n          disabledDescription\n          name\n        }\n      }\n    }\n  }\n",
        "variables": {
            "cartId": cart_id,
        },
    }

    response = requests.post(
        "https://dashboard.boulevard.io/api/v1.0/graph_client",
        headers=headers,
        json=json_data,
    )
    return response.json()["data"]["cart"]["availableCategories"]


def get_providers(headers: Dict[str, str], cart_id: str, item_id: str):
    json_data = {
        "query": "\n  query GetMenuItem($cartToken: ID!, $itemId: ID!) {\n    cart(idOrToken: $cartToken) {\n      availableItem(id: $itemId) {\n        id\n        name\n        description\n        listPriceRange {\n          max\n          min\n          variable\n        }\n        __typename\n        ... on CartAvailableBookableItem {\n          optionGroups {\n            ...OptionGroupFragment\n          }\n          staffVariants {\n            ...StaffVariantFragment\n          }\n          availableAddons {\n            catalogItemId\n            name\n            description\n            disabled\n            disabledDescription\n            listPriceRange {\n              min\n              max\n              variable\n            }\n            staffVariants {\n              ...StaffVariantFragment\n            }\n          }\n        }\n        ... on CartAvailableGiftCardItem {\n          allowCustomAmounts\n          pricePresets\n        }\n      }\n    }\n  }\n  \n  fragment OptionGroupFragment on CartAvailableBookableItemOptionGroup {\n    id\n    name\n    description\n    minLimit\n    maxLimit\n    options {\n      id\n      name\n      description\n      priceDelta\n    }\n    optionProducts {\n      priceDelta\n    }\n  }\n\n  \n  fragment StaffVariantFragment on CartAvailableBookableItemStaffVariant {\n    id\n    price\n    staff {\n      id\n      firstName\n      lastName\n      displayName\n      avatar\n      staffRole {\n        name\n      }\n    }\n  }\n\n",
        "variables": {
            "cartToken": cart_id,
            "itemId": "s_284f87f2-19f9-4fce-b6ea-f7cf5f38b34b",
        },
    }

    response = requests.post(
        "https://dashboard.boulevard.io/api/v1.0/graph_client",
        headers=headers,
        json=json_data,
    )
    return response.json()


def set_provider(
    headers: Dict[str, str], cart_id: str, item_staff_variant_id: str, item_id: str
):
    json_data = {
        "operationName": "cartAddSelectedBookableItem",
        "variables": {
            "input": {
                "idOrToken": cart_id,
                "itemStaffVariantId": item_staff_variant_id,  #'284f87f2-19f9-4fce-b6ea-f7cf5f38b34b:161bd5e9-c48b-4ae2-8050-abc2095cae66',
                "itemId": item_id,  # 's_284f87f2-19f9-4fce-b6ea-f7cf5f38b34b',
                "itemOptionIds": [],
            },
        },
        "query": "mutation cartAddSelectedBookableItem($input: CartAddSelectedBookableItemInput!) {\n  cartAddSelectedBookableItem(input: $input) {\n    cart {\n      ...CartFragment\n      __typename\n    }\n    selectedItem {\n      ...SelectedItemFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CartFragment on Cart {\n  id\n  clientMessage\n  endTime\n  features {\n    accountCreationRequired\n    giftCardPurchaseEnabled\n    waitlistEnabled\n    offersEnabled\n    serviceAddonsEnabled\n    blvdOffsetEnabled\n    __typename\n  }\n  startTime\n  startTimeId\n  advanceGratuity {\n    fixed\n    percentage\n    __typename\n  }\n  clientInformation {\n    email\n    phoneNumber\n    pronoun\n    communicationSubscriptions {\n      key\n      channel\n      enabled\n      __typename\n    }\n    __typename\n  }\n  errors {\n    code\n    __typename\n  }\n  fees {\n    ...CartFeeFragment\n    __typename\n  }\n  guests {\n    ...CartGuestFragment\n    __typename\n  }\n  location {\n    contactEmail\n    featureFlags {\n      covidBookingWarning\n      __typename\n    }\n    id\n    phoneNumber\n    tz\n    __typename\n  }\n  offers {\n    id\n    applied\n    code\n    name\n    discountPercentage\n    discountAmount\n    __typename\n  }\n  selectedItems {\n    id\n    addons {\n      id\n      name\n      description\n      disabled\n      disabledDescription\n      listPriceRange {\n        min\n        max\n        variable\n        __typename\n      }\n      __typename\n    }\n    availablePaymentMethods {\n      ... on CartItemVoucherPaymentMethod {\n        availableCount\n        __typename\n      }\n      __typename\n    }\n    discountAmount\n    item {\n      id\n      name\n      ... on CartAvailableBookableItem {\n        listDuration\n        listPriceRange {\n          max\n          min\n          variable\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    price\n    selectedPaymentMethod {\n      __typename\n      ... on CartItemCardPaymentMethod {\n        cardBrand\n        cardLast4\n        __typename\n      }\n    }\n    __typename\n    ... on CartBookableItem {\n      baseBookableItem {\n        itemId\n        __typename\n      }\n      guestV2 {\n        ...CartGuestFragment\n        __typename\n      }\n      selectedOptions {\n        id\n        name\n        priceDelta\n        __typename\n      }\n      selectedStaffVariant {\n        id\n        staff {\n          displayName\n          id\n          __typename\n        }\n        __typename\n      }\n      startTime\n      __typename\n    }\n    ... on CartGiftCardItem {\n      giftCardDesign {\n        ...CartItemGiftCardDesignFragment\n        __typename\n      }\n      emailFulfillment {\n        ...CartItemEmailFulfillmentFragment\n        __typename\n      }\n      __typename\n    }\n  }\n  fees {\n    percentageAmount\n    absoluteAmount\n    calculatedAmount\n    __typename\n  }\n  summary {\n    discountAmount\n    estimatedDiscountAmountAtCheckout\n    estimatedGratuityAmountAtCheckout\n    estimatedSubtotalAtCheckout\n    estimatedTaxAmountAtCheckout\n    estimatedTotalAtCheckout\n    feeAmount\n    gratuityAmount\n    paymentMethodRequired\n    subtotal\n    taxAmount\n    total\n    depositAmount\n    deposit\n    feeAmount\n    depositFeeAmount\n    depositSubtotal\n    estimatedCancellationFee\n    cancellableBefore\n    __typename\n  }\n  __typename\n}\n\nfragment CartGuestFragment on CartGuest {\n  firstName\n  id\n  label\n  lastName\n  number\n  __typename\n}\n\nfragment CartItemGiftCardDesignFragment on CartItemGiftCardDesign {\n  backgroundColor\n  id\n  image\n  __typename\n}\n\nfragment CartItemEmailFulfillmentFragment on CartItemEmailFulfillment {\n  deliveryDate\n  messageFromSender\n  recipientEmail\n  recipientName\n  senderName\n  __typename\n}\n\nfragment CartFeeFragment on CartFee {\n  absoluteAmount\n  calculatedAmount\n  calculatedTaxAmount\n  id\n  label\n  percentageAmount\n  type\n  __typename\n}\n\nfragment SelectedItemFragment on CartItem {\n  id\n  price\n  ... on CartBookableItem {\n    selectedStaffVariant {\n      id\n      duration\n      staff {\n        avatar\n        displayName\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  item {\n    id\n    name\n    description\n    listPriceRange {\n      max\n      min\n      variable\n      __typename\n    }\n    ... on CartAvailableBookableItem {\n      staffVariants {\n        id\n        staff {\n          avatar\n          displayName\n          __typename\n        }\n        __typename\n      }\n      optionGroups {\n        id\n        description\n        maxLimit\n        minLimit\n        name\n        options {\n          description\n          id\n          name\n          priceDelta\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  addons {\n    id\n    name\n    description\n    disabled\n    disabledDescription\n    listPriceRange {\n      min\n      max\n      variable\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n",
    }

    response = requests.post(
        "https://dashboard.boulevard.io/api/v1.0/graph_client",
        headers=headers,
        json=json_data,
    )
    return response.json()


def get_bookable_dates(
    headers: Dict[str, str],
    cart_id: int,
    n_days: int = 61,
    time_zone: str = "America/New_York",
):
    json_data = {
        "query": "\n  query GetAvailableDates($cartToken: ID!, $from: Date, $limit: Int, $to: Date, $tz: Tz) {\n    cartBookableDates(idOrToken: $cartToken, limit: $limit, searchRangeLower: $from, searchRangeUpper: $to, tz: $tz) {\n      date\n    }\n  }\n",
        "variables": {
            "cartToken": cart_id,
            "limit": n_days,
            "tz": time_zone,
        },
    }

    response = requests.post(
        "https://dashboard.boulevard.io/api/v1.0/graph_client",
        headers=headers,
        json=json_data,
    )
    return response.json()


def clear_cart(headers: Dict[str, str], cart_id: str):
    json_data = {
        "query": "\n  mutation CartClearReservedTime($input: CartClearReservedTimeInput!) {\n    cartClearReservedTime(input: $input) {\n      cart {\n        ...CartFragment\n      }\n    }\n  }\n  \n  fragment CartFragment on Cart {\n    id\n    clientMessage\n    # completedAt\n    endTime\n    features {\n      accountCreationRequired\n      giftCardPurchaseEnabled\n      waitlistEnabled\n      offersEnabled\n      serviceAddonsEnabled\n      blvdOffsetEnabled\n    }\n    startTime\n    startTimeId\n    advanceGratuity {\n      fixed\n      percentage\n    }\n    clientInformation {\n      email\n      phoneNumber\n      pronoun\n      communicationSubscriptions {\n        key\n        channel\n        enabled\n      }\n    }\n    errors {\n      code\n    }\n    fees {\n      ...CartFeeFragment\n    }\n    guests {\n      ...CartGuestFragment\n    }\n    location {\n      contactEmail\n      featureFlags {\n        covidBookingWarning\n      }\n      id\n      phoneNumber\n      tz\n    }\n    offers {\n      id\n      applied\n      code\n      name\n      discountPercentage\n      discountAmount\n    }\n    selectedItems {\n      id\n      addons {\n        id\n        name\n        description\n        disabled\n        disabledDescription\n        listPriceRange {\n          min\n          max\n          variable\n        }\n      }\n      availablePaymentMethods {\n        ... on CartItemVoucherPaymentMethod {\n          availableCount\n          __typename\n        }\n      }\n      discountAmount\n      item {\n        id\n        name\n        ... on CartAvailableBookableItem {\n          listDuration\n          listPriceRange {\n            max\n            min\n            variable\n          }\n        }\n      }\n      price\n      selectedPaymentMethod {\n        __typename\n        ... on CartItemCardPaymentMethod {\n            cardBrand\n            cardLast4\n          }\n      }\n      __typename\n      ... on CartBookableItem {\n        baseBookableItem {\n          itemId\n        }\n        guestV2 {\n          ...CartGuestFragment\n        }\n        selectedOptions {\n          id\n          name\n          priceDelta\n        }\n        selectedStaffVariant {\n          id\n          staff {\n            displayName\n            id\n          }\n        }\n        startTime\n      }\n      ... on CartGiftCardItem {\n        giftCardDesign {\n          ...CartItemGiftCardDesignFragment\n        }\n        emailFulfillment {\n          ...CartItemEmailFulfillmentFragment\n        }\n      }\n    }\n    fees {\n      percentageAmount\n      absoluteAmount\n      calculatedAmount\n    }\n    summary {\n      discountAmount\n      estimatedDiscountAmountAtCheckout\n      estimatedGratuityAmountAtCheckout\n      estimatedSubtotalAtCheckout\n      estimatedTaxAmountAtCheckout\n      estimatedTotalAtCheckout\n      feeAmount\n      gratuityAmount\n      paymentMethodRequired\n      subtotal\n      taxAmount\n      total\n      depositAmount\n      deposit\n      feeAmount\n      depositFeeAmount\n      depositSubtotal\n      estimatedCancellationFee\n      cancellableBefore\n    }\n  }\n  \n  fragment CartGuestFragment on CartGuest {\n    firstName\n    id\n    label\n    lastName\n    number\n  }\n\n  \n  fragment CartItemGiftCardDesignFragment on CartItemGiftCardDesign {\n    backgroundColor\n    id\n    image\n  }\n\n  \n  fragment CartItemEmailFulfillmentFragment on CartItemEmailFulfillment {\n    deliveryDate\n    messageFromSender\n    recipientEmail\n    recipientName\n    senderName\n  }\n\n  \n  fragment CartFeeFragment on CartFee {\n    absoluteAmount\n    calculatedAmount\n    calculatedTaxAmount\n    id\n    label\n    percentageAmount\n    type\n  }\n\n\n",
        "variables": {
            "input": {
                "idOrToken": cart_id,
            },
        },
    }

    response = requests.post(
        "https://dashboard.boulevard.io/api/v1.0/graph_client",
        headers=headers,
        json=json_data,
    )
    return response.json()


def get_times(
    headers: Dict[str, str],
    cart_token: str,
    search_date: str,
    time_zone: str = "America/New_York",
):
    # TODO:: SET TIMEZONE
    json_data = {
        "query": "\n  query GetAvailableTimes($cartToken: ID!, $searchDate: Date!, $tz: Tz) {\n    cartBookableTimes(idOrToken: $cartToken, searchDate: $searchDate, tz: $tz) {\n      id\n      score\n      startTime\n    }\n  }\n",
        "variables": {
            "cartToken": cart_token,
            "searchDate": search_date,
            "tz": time_zone,
        },
    }

    response = requests.post(
        "https://dashboard.boulevard.io/api/v1.0/graph_client",
        headers=headers,
        json=json_data,
    )
    return response.json()
