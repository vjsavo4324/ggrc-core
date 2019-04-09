/*
    Copyright (C) 2019 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import {initWidgets} from '../../plugins/utils/widgets-utils';
import {gapiClient} from '../../plugins/ggrc-gapi-client';

gapiClient.loadGapiClient();

$('#csv_import').html(can.stache('<csv-import/>'));
$('#page-header').html(can.stache('<page-header/>'));
initWidgets();
