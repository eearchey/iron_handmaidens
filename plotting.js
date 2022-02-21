// https://danfo.jsdata.org/api-reference/plotting/line-charts
async function plotCSV(divId, fileName) {
	let df = await dfd.readCSV(fileName);

	df.config['tableMaxRow'] = 2;
	df.config['tableDisplayConfig'] = {
		header: {
			alignment: 'center',
			content: 'Table from ' + fileName
		}
	};
	df.print();

	df = df.setIndex({column: 'Timestamp_4680', drop: true});
	df.plot(divId).line({
		config: {
			columns: ['CH1_4680', 'CH2_4680']
		}
	});
}
