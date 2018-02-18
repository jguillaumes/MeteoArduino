/*
 * DataRecorder.h
 *
 *  Created on: Feb 18, 2018
 *      Author: jguillaumes
 */

#ifndef DATARECORDER_H_
#define DATARECORDER_H_

#include <SPI.h>
#include <SPISRAM.h>

#define DR_CATCHER	"DATARECD"
#define DR_VERSION  "01.00.00"

class DataRecorder {
public:
	enum Error {OK=0, BADCATCHER, BADADDR, BADREC, BADKEY, NOTFND, IOERR};
	struct dr_item {
		uint64_t itemKey;
		byte *itemData;
	};
	DataRecorder(int itemSize, int cspin1=9, int cspin2=10);
	virtual ~DataRecorder();
	bool begin();
	void initialize();
	bool addItem(struct dr_item *item);
	bool addItem(uint64_t key, byte *data);
	bool getItem(const uint32_t numItem, struct dr_item *item);
	bool getItem(const uint64_t key, struct dr_item *item);
	bool replaceItem(const uint32_t numItem, struct dr_item *item);
	bool replaceItem(const uint64_t key, struct dr_item *item);
	uint32_t getNumItems() { return _header.itemCount; }
	uint64_t getFirstKey() { return _header.keyFirst; }
	uint64_t getLastKey() { return _header.keyLast; }

protected:
	const uint32_t DATA_START = sizeof(struct dr_header);

private:
	struct dr_header {
		char eyecatcher[8];
		char hdrVersion[8];
		uint32_t itemSize;
		uint32_t itemCount;
		uint32_t itemFirst;
		uint32_t itemLast;
		uint64_t keyFirst;
		uint64_t keyLast;
		char free[16];
	};
	struct locator {
		SPISRAM *chip;
		uint32_t physAddress;
	};
	typedef struct locator locator_t;
	struct dr_header _header;
	SPISRAM *_chip1;
	SPISRAM *_chip2;
	uint32_t _capacity;
	enum Error _lastError;

	uint32_t getAddress(const uint32_t numItem);
	locator_t getLocator(const uint32_t address);
	bool readKey(const uint32_t addr, uint64_t &key);
	bool putKey(const uint32_t addr, const uint64_t key);
	bool readHeader();
	bool newHeader();
	bool writeHeader();

};

#endif /* DATARECORDER_H_ */
